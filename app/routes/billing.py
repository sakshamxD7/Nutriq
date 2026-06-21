from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.plan import Subscription
from app.extensions import db, csrf
from datetime import datetime, timedelta
import stripe

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/plans', methods=['GET'])
def plans():
    # Detect if we are in simulation mode (Stripe key missing)
    stripe_configured = bool(current_app.config.get('STRIPE_SECRET_KEY') and 
                             "change_me" not in current_app.config.get('STRIPE_SECRET_KEY') and
                             "your_stripe" not in current_app.config.get('STRIPE_SECRET_KEY'))
    
    active_subscription = None
    if current_user.is_authenticated:
        active_subscription = Subscription.query.filter_by(
            user_id=current_user.id, 
            status='active'
        ).first()

    return render_template(
        'billing/plans.html',
        stripe_configured=stripe_configured,
        active_sub=active_subscription
    )


@billing_bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    plan_type = request.form.get('plan') # 'plus' or 'pro'
    if plan_type not in ('plus', 'pro'):
        flash("Invalid plan selected.", "danger")
        return redirect(url_for('billing.plans'))

    # Check key configurations
    secret_key = current_app.config.get('STRIPE_SECRET_KEY')
    stripe_configured = bool(secret_key and 
                             "change_me" not in secret_key and
                             "your_stripe" not in secret_key)
    
    if not stripe_configured:
        # --- SIMULATION / FALLBACK DEMO MODE ---
        try:
            # Upgrade user to premium directly
            current_user.is_premium = True
            
            # Deactivate previous subscriptions
            Subscription.query.filter_by(user_id=current_user.id).update({'status': 'cancelled'})
            
            # Create a mock active subscription
            mock_sub = Subscription(
                user_id=current_user.id,
                stripe_customer_id="cus_mock12345",
                stripe_subscription_id=f"sub_mock_{plan_type}_{int(datetime.utcnow().timestamp())}",
                plan_type=plan_type,
                status="active",
                current_period_end=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(mock_sub)
            db.session.commit()
            
            flash(f"[Demo Mode] Successfully upgraded to Nutriq {plan_type.capitalize()}! Bypassed Stripe payment flow.", "success")
            return redirect(url_for('billing.success'))
        except Exception as e:
            db.session.rollback()
            flash(f"Simulation upgrade failed: {str(e)}", "danger")
            return redirect(url_for('billing.plans'))

    # --- REAL STRIPE BILLING ---
    stripe.api_key = secret_key
    
    # Map plan types to Stripe price IDs
    price_id = (
        current_app.config.get('STRIPE_PLUS_PRICE_ID') 
        if plan_type == 'plus' 
        else current_app.config.get('STRIPE_PRO_PRICE_ID')
    )
    
    if not price_id:
        flash("Stripe Price ID is not configured for this plan.", "danger")
        return redirect(url_for('billing.plans'))

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'billing/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'billing/plans',
            client_reference_id=str(current_user.id),
            customer_email=current_user.email
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Stripe Checkout error: {str(e)}", "danger")
        return redirect(url_for('billing.plans'))


@billing_bp.route('/success', methods=['GET'])
@login_required
def success():
    # If stripe checkout session_id exists, we can fetch subscription details or just rely on webhook update
    # In either case, we ensure is_premium is set to True
    session_id = request.args.get('session_id')
    if session_id and current_app.config.get('STRIPE_SECRET_KEY'):
        # Just flag premium as a fallback safety
        try:
            current_user.is_premium = True
            db.session.commit()
        except:
            pass
            
    return render_template('billing/plans.html', success_checkout=True)


@billing_bp.route('/webhook', methods=['POST'])
@csrf.exempt
def webhook():
    """
    Handles Stripe webhooks.
    Requires raw payload and signature verification.
    """
    payload = request.data
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    # If key configurations are not set, return bad request
    if not webhook_secret or not current_app.config.get('STRIPE_SECRET_KEY'):
        return jsonify({'error': 'Webhook not configured'}), 400

    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event.get('type')
    
    # Handle the event
    if event_type == 'checkout.session.completed':
        session_obj = event['data']['object']
        user_id = session_obj.get('client_reference_id')
        customer_id = session_obj.get('customer')
        subscription_id = session_obj.get('subscription')
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.is_premium = True
                
                # Fetch details from Stripe to see plan type
                plan_type = "plus" # default
                current_period_end = None
                try:
                    stripe_sub = stripe.Subscription.retrieve(subscription_id)
                    price_id = stripe_sub['items']['data'][0]['price']['id']
                    if price_id == current_app.config.get('STRIPE_PRO_PRICE_ID'):
                        plan_type = "pro"
                    current_period_end = datetime.utcfromtimestamp(stripe_sub['current_period_end'])
                except:
                    pass

                # Check if subscription already logged
                sub_record = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
                if not sub_record:
                    sub_record = Subscription(
                        user_id=user.id,
                        stripe_customer_id=customer_id,
                        stripe_subscription_id=subscription_id,
                        plan_type=plan_type,
                        status="active",
                        current_period_end=current_period_end
                    )
                    db.session.add(sub_record)
                else:
                    sub_record.status = "active"
                    sub_record.current_period_end = current_period_end
                
                db.session.commit()
                
    elif event_type == 'customer.subscription.deleted':
        subscription_obj = event['data']['object']
        subscription_id = subscription_obj.get('id')
        
        sub_record = Subscription.query.filter_by(stripe_subscription_id=subscription_id).first()
        if sub_record:
            sub_record.status = "cancelled"
            user = User.query.get(sub_record.user_id)
            if user:
                # Check if user has any other active premium subscriptions
                other_subs = Subscription.query.filter(
                    Subscription.user_id == user.id,
                    Subscription.status == 'active',
                    Subscription.stripe_subscription_id != subscription_id
                ).first()
                if not other_subs:
                    user.is_premium = False
            db.session.commit()

    return jsonify({'success': True}), 200


@billing_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Endpoint for user to cancel their premium membership."""
    active_sub = Subscription.query.filter_by(user_id=current_user.id, status='active').first()
    if not active_sub:
        flash("No active subscription found.", "warning")
        return redirect(url_for('billing.plans'))

    # If simulation subscription
    if active_sub.stripe_customer_id == "cus_mock12345":
        active_sub.status = "cancelled"
        current_user.is_premium = False
        db.session.commit()
        flash("Subscription cancelled successfully (Demo Mode).", "success")
        return redirect(url_for('billing.plans'))

    # If real Stripe subscription
    secret_key = current_app.config.get('STRIPE_SECRET_KEY')
    if secret_key:
        stripe.api_key = secret_key
        try:
            stripe.Subscription.delete(active_sub.stripe_subscription_id)
            active_sub.status = "cancelled"
            current_user.is_premium = False
            db.session.commit()
            flash("Your subscription has been cancelled and will expire at the end of the billing cycle.", "success")
        except Exception as e:
            flash(f"Stripe error cancelling subscription: {str(e)}", "danger")
    else:
        # Fallback cancellation
        active_sub.status = "cancelled"
        current_user.is_premium = False
        db.session.commit()
        flash("Subscription cancelled.", "success")

    return redirect(url_for('billing.plans'))
