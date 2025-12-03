# LMS Memberships

A Frappe application that adds membership/subscription functionality to [Frappe LMS](https://github.com/frappe/lms). This app allows you to create membership tiers, manage subscriptions, and provide access control to courses based on membership status.

## Features

### 🎫 Membership Tiers
- Create multiple membership tiers (e.g., Basic, Premium, Enterprise)
- Set custom pricing and duration for each tier
- Define which courses are accessible per tier or enable access to all courses
- Add tier-specific benefits and descriptions

### 💳 Payment Integration
- Integrated with Midtrans payment gateway (extensible to other gateways)
- Secure payment processing with callback handling
- Pending payment recovery and retry functionality

### 👥 User Membership Management
- Track active, pending, expired, and cancelled memberships
- Automatic membership activation upon successful payment
- Email notifications for membership confirmation
- Expiry warnings and renewal reminders

### 🎨 Frontend Vue Overrides
- Custom membership plans page at `/lms/membership`
- Membership banner on home page, courses page
- Membership status card on user profile
- Fully integrated with LMS Vue frontend using override pattern

## Installation

### Prerequisites
- Frappe Bench v15+
- Frappe LMS app installed
- Node.js 18+ and Yarn (for building frontend)
- A payment gateway configured (e.g., Midtrans via `payment_midtrans` app)

### Install via Bench

```bash
# Get the app
bench get-app https://github.com/your-org/lms_memberships.git

# Install on your site
bench --site your-site.localhost install-app lms_memberships
```

### Build Frontend Assets

**Important:** Frontend assets are not included in the repository and must be built after installation.

```bash
# Navigate to frontend directory
cd apps/lms_memberships/frontend

# Install dependencies
yarn install --ignore-engines

# Build frontend (requires increased memory for large bundles)
NODE_OPTIONS="--max-old-space-size=4096" yarn build

# Return to bench directory and build Frappe assets
cd ../../../
bench build --app lms_memberships

# Clear cache
bench --site your-site.localhost clear-cache
```

### Docker Deployment

When building a custom Docker image, add these commands to your Dockerfile or build script:

```dockerfile
# Build lms_memberships frontend
RUN cd /home/frappe/frappe-bench/apps/lms_memberships/frontend && \
    yarn install --ignore-engines && \
    NODE_OPTIONS="--max-old-space-size=4096" yarn build

# Build Frappe assets
RUN cd /home/frappe/frappe-bench && bench build --app lms_memberships
```

## Configuration

### 1. Create Membership Tiers

Go to **LMS Memberships > LMS Membership Tier** and create your tiers:

| Field | Description |
|-------|-------------|
| Tier Name | Display name (e.g., "Premium Monthly") |
| Description | Brief description shown to users |
| Price | Subscription price |
| Currency | Payment currency (e.g., IDR, USD) |
| Duration (Months) | How long the membership lasts |
| Access All Courses | Toggle to grant access to all courses |
| Courses | If not all courses, select specific courses |
| Benefits | Bullet-pointed list of tier benefits |
| Is Active | Enable/disable the tier |
| Is Default | Mark as recommended tier |

### 2. Configure Payment Gateway

1. Go to **LMS Settings**
2. Set the **Payment Gateway** (e.g., "Midtrans")
3. Ensure your payment gateway app is properly configured

### 3. Frontend Override

The app automatically overrides the LMS frontend to add membership functionality. The override happens via `www/lms.html` which takes precedence over the original LMS file.

## DocTypes

### LMS Membership Tier
Defines available membership plans with pricing, duration, and course access settings.

**Fields:**
- `tier_name`: Name of the tier
- `description`: Tier description
- `price`: Subscription price
- `currency`: Payment currency
- `duration_months`: Membership duration
- `access_all_courses`: Boolean for full course access
- `courses`: Child table for specific course access
- `benefits`: Text field for tier benefits
- `is_active`: Enable/disable tier
- `is_default`: Mark as recommended

### LMS User Membership
Tracks individual user subscriptions.

**Fields:**
- `member`: Link to User
- `membership_tier`: Link to LMS Membership Tier
- `status`: Pending, Active, Expired, Cancelled
- `start_date`: Membership start date
- `end_date`: Membership end date
- `amount_paid`: Payment amount
- `currency`: Payment currency
- `payment_reference`: Payment gateway reference
- `order_id`: Order ID for payment tracking

## API Reference

### Public APIs (allow_guest=True)

#### `get_membership_tiers()`
Returns all active membership tiers with their details.

```python
tiers = frappe.call('lms_memberships.api.membership.get_membership_tiers')
```

#### `get_user_membership_status(user_email=None)`
Get membership status for a user. If `user_email` is not provided, returns status for the current logged-in user.

```python
status = frappe.call('lms_memberships.api.membership.get_user_membership_status', 
                     user_email='user@example.com')
```

**Response:**
```json
{
  "has_active_membership": true,
  "tier_name": "Premium",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "days_remaining": 180,
  "is_expiring_soon": false
}
```

### Authenticated APIs

#### `create_membership_payment(tier_name, address=None)`
Initiate payment for a membership tier. Returns payment URL.

#### `retry_pending_payment(membership_name)`
Retry payment for a pending membership.

#### `cancel_pending_membership(membership_name)`
Cancel a pending membership.

#### `get_pending_membership()`
Get user's pending membership if any.

#### `has_course_access(course_name)`
Check if user has access to a specific course through membership.

#### `get_accessible_courses()`
Get all courses accessible through user's membership.

## Frontend Structure

The app uses a Vue override pattern to extend the LMS frontend without modifying the original LMS source code.

```
frontend/
├── custom-build.js          # Copies LMS src, applies overrides
├── package.json             # Build scripts and dependencies
├── vite.config.js           # Vite build configuration
├── tailwind.config.cjs      # Tailwind CSS configuration
├── postcss.config.cjs       # PostCSS configuration
├── src_override/            # Override files
│   ├── router.js            # Adds /membership route
│   ├── components/
│   │   └── MembershipBanner.vue
│   └── pages/
│       ├── Membership.vue   # Membership plans page
│       ├── Courses.vue      # Override with banner
│       ├── ProfileAbout.vue # Override with membership card
│       └── Home/
│           ├── StudentHome.vue
│           └── AdminHome.vue
```

### Build Process

1. `yarn prepare-src` - Copies original LMS frontend src to `./src`
2. Overlays `./src_override` files on top
3. `yarn build` - Compiles to `../lms_memberships/public/frontend/`
4. Frappe-ui plugin updates `www/lms.html` with correct asset paths

## Customization

### Styling

The membership components use a navy blue theme (`from-blue-900 to-blue-700`). To customize:

1. Edit the Vue components in `frontend/src_override/`
2. Modify Tailwind classes as needed
3. Rebuild: `yarn build`

### Adding New Tiers

Tiers are managed through the DocType, no code changes required. Simply create new **LMS Membership Tier** records.

### Payment Gateway

To use a different payment gateway:

1. Install the payment gateway app
2. Update **LMS Settings > Payment Gateway**
3. Ensure the gateway implements the required interface

## Development

### Prerequisites
- Node.js 18+
- Yarn
- Python 3.10+

### Setup Development Environment

```bash
# Clone the repository
cd apps/lms_memberships/frontend

# Install dependencies
yarn install --ignore-engines

# Prepare source (copies LMS frontend + applies overrides)
yarn prepare-src

# Start development server
yarn dev
```

### Building for Production

```bash
# Build with increased memory limit
NODE_OPTIONS="--max-old-space-size=4096" yarn build

# Build Frappe assets
cd ../../../
bench build --app lms_memberships
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/lms_memberships
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## Troubleshooting

### Frontend not loading
1. Check if assets are built: `ls lms_memberships/public/frontend/assets/`
2. Run `bench build --app lms_memberships`
3. Clear cache: `bench --site your-site.localhost clear-cache`

### Payment not processing
1. Check payment gateway configuration
2. Review error logs: `bench --site your-site.localhost show-error-log`
3. Verify callback URL is accessible

### Membership not activating
1. Check `LMS User Membership` status
2. Verify payment callback received
3. Check `order_id` matches between payment and membership

## License

MIT License - See [LICENSE](license.txt) for details.

## Support

For issues and feature requests, please use the GitHub Issues page.
