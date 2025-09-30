# Text-to-Workout Flask App

## Overview
A minimalistic Flask web application that generates cycling workout files (.zwo, .mrc) with Free and Pro modes.

## Current Status (MVP/Prototype)
- **Frontend**: HTMX + Tailwind CSS (CDN)
- **Backend**: Flask with Stripe integration
- **Features**: Free mode (dropdown-based), Pro mode (text-based - currently dummy), workout previews, file downloads

## Architecture
- `app.py`: Main Flask application with all routes
- `templates/`: Jinja2 templates with HTMX partials
- `templates/partials/`: HTMX response templates
- `.env.example`: Environment variable template

## Routes
- `GET /`: Landing page with Free/Pro forms
- `POST /preview`: HTMX endpoint for workout preview (returns partial HTML)
- `GET /download`: File download endpoint (.zwo/.mrc formats)
- `POST /checkout`: Stripe Checkout session creation
- `POST /webhook/billing`: Stripe webhook handler
- `GET /success`: Payment success page
- `GET /cancel`: Payment cancelled page

## Environment Variables
- `SESSION_SECRET`: Flask session secret
- `STRIPE_SECRET`: Stripe API secret key
- `STRIPE_PRICE_ID`: Stripe subscription price ID
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret
- `LLM_API_KEY`: LLM API key for Pro text-to-workout (not yet implemented)
- `PLAUSIBLE_DOMAIN`: Analytics domain (optional)
- `SENTRY_DSN`: Error monitoring DSN (optional)

## Known Limitations (Prototype)
1. **Pro Access Control**: Current session-based Pro gating is for prototype only. Production needs:
   - Proper user authentication system
   - Database-backed user/subscription tracking
   - Stripe session verification on success route
   - Webhook integration with persistent user records

2. **LLM Integration**: Pro mode text-to-workout uses dummy data. Next phase requires:
   - LLM API integration (OpenAI/Anthropic)
   - Prompt engineering for workout generation
   - Structured workout parsing

3. **Workout Files**: Current .zwo/.mrc files are simplified templates. Future:
   - Complex interval structures
   - FTP-based zone calculations
   - Custom workout file formats

## Next Phase Features
- User authentication and account management
- Database integration for user/subscription data
- Real LLM-powered workout generation from text
- Advanced workout file generation with proper intervals
- Plausible Analytics integration
- Sentry error monitoring
- Production deployment configuration

## Development
- Run: `python app.py`
- Server: http://0.0.0.0:5000
- Debug mode enabled for development
