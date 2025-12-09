# Building Frontend After Changes

This document explains how to build the frontend after making changes to override files.

## Prerequisites

Both `lms` and `lms_memberships` apps must be installed in the same Frappe bench:

```bash
# Get both apps
bench get-app https://github.com/frappe/lms.git
bench get-app https://github.com/ptrmtb/lms_memberships.git

# Install on your site
bench --site your-site.localhost install-app lms
bench --site your-site.localhost install-app lms_memberships
```

## Building After Changes

After modifying any files in `frontend/src_override/`, rebuild the frontend:

```bash
# Navigate to the frontend directory
cd apps/lms_memberships/frontend

# Install dependencies (if not already done)
yarn install --ignore-engines

# Build the frontend
yarn build
```

### What the Build Process Does

1. **Copies LMS Source**: `custom-build.js` copies the original LMS frontend from `apps/lms/frontend/src` to `apps/lms_memberships/frontend/src`
2. **Applies Overrides**: Copies all files from `src_override/` on top of the copied source, replacing matching files
3. **Builds Assets**: Vite compiles the combined source to `lms_memberships/public/frontend/`
4. **Updates HTML**: The Frappe UI Vite plugin updates `lms_memberships/www/lms.html` with correct asset paths

### Committing Changes

After building, commit the updated assets:

```bash
cd apps/lms_memberships
git add lms_memberships/public/frontend/
git add lms_memberships/www/lms.html
git commit -m "build: update frontend assets after [your change]"
git push
```

## Recent Changes

### CourseCardOverlay Membership Check

**File**: `frontend/src_override/components/CourseCardOverlay.vue`

**Change**: Added membership access check to hide "Buy this course" button for users with `access_all_courses` membership.

**Implementation**:
- Calls `lms_memberships.api.membership.has_course_access()` on component mount
- Shows "Included in Membership" badge if user has access via membership
- Shows "Start Learning" button to directly enroll (since they have access)
- Falls back to "Buy this course" button if no membership access

**To deploy**:
```bash
cd apps/lms_memberships/frontend
yarn build
cd ..
git add lms_memberships/public/frontend/ lms_memberships/www/lms.html
git commit -m "build: add membership check to course detail page"
```

## Development Mode

For development with hot reload:

```bash
cd apps/lms_memberships/frontend
yarn dev
```

This starts a Vite dev server with hot module replacement. The dev server proxies API calls to your Frappe site.

## Troubleshooting

### Error: Cannot find LMS source

```
Error: ENOENT: no such file or directory, lstat '/path/to/lms/frontend/src'
```

**Solution**: Ensure the `lms` app is installed in the same bench:
```bash
bench get-app https://github.com/frappe/lms.git
```

### Assets not updating

**Solution**: Clear cache after building:
```bash
bench --site your-site.localhost clear-cache
```

Also hard refresh your browser (Ctrl+Shift+R).

### Node version issues

The build process requires Node.js 18+. If you see version errors:
```bash
nvm install 18
nvm use 18
```
