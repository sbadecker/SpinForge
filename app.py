import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, session
from dotenv import load_dotenv
import stripe
from stripe.error import SignatureVerificationError
from io import BytesIO
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')

stripe.api_key = os.getenv('STRIPE_SECRET')
STRIPE_PRICE_ID = os.getenv('STRIPE_PRICE_ID', 'price_xxx')
PLAUSIBLE_DOMAIN = os.getenv('PLAUSIBLE_DOMAIN', '')
SENTRY_DSN = os.getenv('SENTRY_DSN', '')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

WORKOUT_CONFIGS = {
    '30_endurance': {'duration': 30, 'focus': 'Endurance', 'if': 0.65, 'tss': 20},
    '30_sweetspot': {'duration': 30, 'focus': 'Sweet Spot', 'if': 0.88, 'tss': 38},
    '30_threshold': {'duration': 30, 'focus': 'Threshold', 'if': 0.95, 'tss': 45},
    '30_vo2': {'duration': 30, 'focus': 'VO2 Max', 'if': 1.05, 'tss': 55},
    '45_endurance': {'duration': 45, 'focus': 'Endurance', 'if': 0.65, 'tss': 30},
    '45_sweetspot': {'duration': 45, 'focus': 'Sweet Spot', 'if': 0.88, 'tss': 57},
    '45_threshold': {'duration': 45, 'focus': 'Threshold', 'if': 0.95, 'tss': 68},
    '45_vo2': {'duration': 45, 'focus': 'VO2 Max', 'if': 1.05, 'tss': 82},
    '60_endurance': {'duration': 60, 'focus': 'Endurance', 'if': 0.65, 'tss': 40},
    '60_sweetspot': {'duration': 60, 'focus': 'Sweet Spot', 'if': 0.88, 'tss': 76},
    '60_threshold': {'duration': 60, 'focus': 'Threshold', 'if': 0.95, 'tss': 90},
    '60_vo2': {'duration': 60, 'focus': 'VO2 Max', 'if': 1.05, 'tss': 110},
    '75_endurance': {'duration': 75, 'focus': 'Endurance', 'if': 0.65, 'tss': 50},
    '75_sweetspot': {'duration': 75, 'focus': 'Sweet Spot', 'if': 0.88, 'tss': 95},
    '75_threshold': {'duration': 75, 'focus': 'Threshold', 'if': 0.95, 'tss': 113},
    '75_vo2': {'duration': 75, 'focus': 'VO2 Max', 'if': 1.05, 'tss': 138},
    '90_endurance': {'duration': 90, 'focus': 'Endurance', 'if': 0.65, 'tss': 60},
    '90_sweetspot': {'duration': 90, 'focus': 'Sweet Spot', 'if': 0.88, 'tss': 114},
    '90_threshold': {'duration': 90, 'focus': 'Threshold', 'if': 0.95, 'tss': 135},
    '90_vo2': {'duration': 90, 'focus': 'VO2 Max', 'if': 1.05, 'tss': 165},
}

@app.route('/')
def index():
    is_pro = session.get('is_pro', False)
    return render_template('index.html', is_pro=is_pro, plausible_domain=PLAUSIBLE_DOMAIN)

@app.route('/preview', methods=['POST'])
def preview():
    mode = request.form.get('mode', 'free')
    is_pro = session.get('is_pro', False)
    
    if mode == 'pro' and not is_pro:
        return render_template('partials/preview.html', error='Pro-Features benötigen ein Abonnement'), 403
    
    if mode == 'free':
        duration = request.form.get('duration', '60')
        focus = request.form.get('focus', 'Endurance')
        config_key = f"{duration}_{focus.lower().replace(' ', '')}"
        workout = WORKOUT_CONFIGS.get(config_key, WORKOUT_CONFIGS['60_endurance'])
    else:
        custom_text = request.form.get('custom_text', '')
        workout = {
            'duration': 60,
            'focus': 'Custom',
            'if': 0.85,
            'tss': 72,
            'custom_text': custom_text
        }
    
    zones = generate_zone_bars(workout)
    
    return render_template('partials/preview.html', 
                         workout=workout, 
                         zones=zones,
                         mode=mode)

@app.route('/download')
def download():
    fmt = request.args.get('fmt', 'zwo')
    duration = int(request.args.get('duration', '60'))
    focus = request.args.get('focus', 'Endurance')
    intensity = float(request.args.get('if', '0.85'))
    mode = request.args.get('mode', 'free')
    
    if fmt == 'zwo':
        content = generate_zwo(duration, focus, intensity)
        mimetype = 'application/xml'
        filename = f'workout_{focus.lower()}_{duration}min.zwo'
    else:
        content = generate_mrc(duration, focus, intensity)
        mimetype = 'text/plain'
        filename = f'workout_{focus.lower()}_{duration}min.mrc'
    
    return send_file(
        BytesIO(content.encode('utf-8')),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'success',
            cancel_url=request.host_url + 'cancel',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/billing', methods=['POST'])
def webhook_billing():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        customer_id = session_data.get('customer')
        session['is_pro'] = True
        session['stripe_customer_id'] = customer_id
        logger.info(f"Pro subscription activated for customer {customer_id}")
    
    elif event['type'] == 'customer.subscription.deleted':
        session_data = event['data']['object']
        customer_id = session_data.get('customer')
        session['is_pro'] = False
        logger.info(f"Pro subscription cancelled for customer {customer_id}")
    
    return jsonify({'status': 'success'}), 200

@app.route('/success')
def success():
    session['is_pro'] = True
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

def generate_zone_bars(workout):
    focus = workout['focus'].lower().replace(' ', '')
    duration = workout['duration']
    
    if focus == 'endurance':
        return [
            {'zone': 'Z2', 'percentage': 100, 'color': 'bg-green-500'},
        ]
    elif focus == 'sweetspot':
        return [
            {'zone': 'Z2', 'percentage': 30, 'color': 'bg-green-500'},
            {'zone': 'Z3', 'percentage': 50, 'color': 'bg-yellow-500'},
            {'zone': 'Z2', 'percentage': 20, 'color': 'bg-green-500'},
        ]
    elif focus == 'threshold':
        return [
            {'zone': 'Z2', 'percentage': 20, 'color': 'bg-green-500'},
            {'zone': 'Z4', 'percentage': 60, 'color': 'bg-orange-500'},
            {'zone': 'Z2', 'percentage': 20, 'color': 'bg-green-500'},
        ]
    elif focus == 'vo2max' or focus == 'vo2':
        return [
            {'zone': 'Z2', 'percentage': 15, 'color': 'bg-green-500'},
            {'zone': 'Z5', 'percentage': 40, 'color': 'bg-red-500'},
            {'zone': 'Z2', 'percentage': 30, 'color': 'bg-green-500'},
            {'zone': 'Z5', 'percentage': 15, 'color': 'bg-red-500'},
        ]
    else:
        return [
            {'zone': 'Z2', 'percentage': 50, 'color': 'bg-blue-500'},
            {'zone': 'Z3', 'percentage': 50, 'color': 'bg-yellow-500'},
        ]

def generate_zwo(duration, focus, intensity):
    zwo = f'''<workout_file>
    <author>RoadForge</author>
    <name>{focus} - {duration} min</name>
    <description>Auto-generated {focus} workout</description>
    <sportType>bike</sportType>
    <tags>
        <tag name="{focus.lower()}"/>
    </tags>
    <workout>
        <Warmup Duration="300" PowerLow="0.50" PowerHigh="0.75"/>
        <SteadyState Duration="{(duration - 10) * 60}" Power="{intensity:.2f}"/>
        <Cooldown Duration="300" PowerLow="0.70" PowerHigh="0.50"/>
    </workout>
</workout_file>'''
    return zwo

def generate_mrc(duration, focus, intensity):
    mrc = f'''[COURSE HEADER]
VERSION = 2
UNITS = ENGLISH
DESCRIPTION = {focus} - {duration} min
FILE NAME = workout_{focus.lower()}
MINUTES PERCENT
[END COURSE HEADER]
[COURSE DATA]
0.00    50
5.00    75
5.00    {int(intensity * 100)}
{duration - 5:.2f}    {int(intensity * 100)}
{duration:.2f}    50
[END COURSE DATA]'''
    return mrc

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
