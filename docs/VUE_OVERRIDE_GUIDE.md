# Vue Override Guide for Frappe Applications

This comprehensive guide explains how to override Vue.js frontend components in Frappe applications (like LMS, CRM, Helpdesk) from a custom app without modifying the original source code.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Architecture Overview](#architecture-overview)
4. [Setting Up the Override System](#setting-up-the-override-system)
5. [Directory Structure](#directory-structure)
6. [The Build Process Explained](#the-build-process-explained)
7. [Overriding Components](#overriding-components)
8. [Overriding Pages](#overriding-pages)
9. [Adding New Routes](#adding-new-routes)
10. [Serving the Custom Frontend](#serving-the-custom-frontend)
11. [Development Workflow](#development-workflow)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)
14. [Examples](#examples)

---

## Introduction

### The Problem

Frappe applications like LMS, CRM, and Helpdesk have Vue.js frontends that are separate from the traditional Jinja-based web interface. When you need to customize these frontends, directly modifying the source code creates maintenance nightmares:

- Your changes get overwritten during updates
- You can't easily track what you've modified
- Merging upstream changes becomes difficult

### The Solution

The Vue Override pattern allows you to:

- Keep the original app's source code untouched
- Apply your customizations from a separate custom app
- Easily update the original app without losing changes
- Track all your modifications in your own repository

This pattern was pioneered by projects like [crm_override](https://github.com/esafwan/crm_override) and is now a recommended approach for Frappe Vue customizations.

---

## Prerequisites

Before implementing Vue overrides, ensure you have:

1. **Frappe Bench** setup and running
2. **Node.js** (v18 or later recommended)
3. **Yarn** package manager
4. A **custom Frappe app** created via `bench new-app`
5. The **target app** (e.g., LMS) installed in your bench

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BUILD PROCESS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Original App (LMS)          Custom App (lms_memberships)       │
│   ─────────────────           ────────────────────────────       │
│   apps/lms/frontend/          apps/lms_memberships/frontend/     │
│   └── src/                    ├── src_override/                  │
│       ├── router.js           │   ├── router.js                  │
│       ├── pages/              │   ├── pages/                     │
│       │   └── Home.vue        │   │   └── Home.vue (modified)    │
│       └── components/         │   └── components/                │
│                               │       └── NewComponent.vue       │
│            │                  │                                  │
│            │                  │                                  │
│            ▼                  ▼                                  │
│   ┌─────────────────────────────────────────────────────┐        │
│   │              custom-build.js                        │        │
│   │  1. Copy original src/ → custom app's src/          │        │
│   │  2. Overlay src_override/ files on top              │        │
│   └─────────────────────────────────────────────────────┘        │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────┐        │
│   │              vite.config.js                         │        │
│   │  Build the merged source and output to:             │        │
│   │  lms_memberships/public/frontend/                   │        │
│   └─────────────────────────────────────────────────────┘        │
│                              │                                   │
│                              ▼                                   │
│   ┌─────────────────────────────────────────────────────┐        │
│   │              www/lms.html + lms.py                  │        │
│   │  Override the entry point to serve custom build     │        │
│   └─────────────────────────────────────────────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Setting Up the Override System

### Step 1: Create Frontend Directory Structure

```bash
cd apps/your_custom_app
mkdir -p frontend/src_override
```

### Step 2: Create package.json

Create `frontend/package.json`:

```json
{
  "name": "your-custom-app-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "prepare-src": "node custom-build.js",
    "prebuild": "yarn prepare-src",
    "build": "vite build --base=/assets/your_custom_app/frontend/",
    "predev": "yarn prepare-src",
    "dev": "vite --host"
  },
  "dependencies": {},
  "devDependencies": {
    "fs-extra": "^11.2.0",
    "glob": "^10.3.10"
  }
}
```

> **Note:** The `dependencies` and `devDependencies` lists are kept minimal. The original app's dependencies will be used during build.

### Step 3: Create custom-build.js

This is the heart of the override system. Create `frontend/custom-build.js`:

```javascript
/**
 * Custom Build Script for Vue Frontend Overrides
 * 
 * This script:
 * 1. Copies the entire src/ directory from the original app
 * 2. Overlays your custom files from src_override/ on top
 * 
 * Files in src_override/ replace files in the original src/ if they
 * have the same path, or are added as new files.
 */

import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration - adjust these paths for your setup
const ORIGINAL_APP_NAME = 'lms';  // The app you're overriding
const ORIGINAL_SRC = path.resolve(__dirname, `../../${ORIGINAL_APP_NAME}/frontend/src`);
const CUSTOM_SRC = path.resolve(__dirname, 'src_override');
const TARGET_SRC = path.resolve(__dirname, 'src');

async function prepareSrc() {
    console.log('🔧 Preparing source files...');
    console.log(`   Original source: ${ORIGINAL_SRC}`);
    console.log(`   Override source: ${CUSTOM_SRC}`);
    console.log(`   Target: ${TARGET_SRC}`);

    // Step 1: Remove existing src directory
    if (fs.existsSync(TARGET_SRC)) {
        console.log('🗑️  Removing existing src directory...');
        await fs.remove(TARGET_SRC);
    }

    // Step 2: Copy original source
    if (!fs.existsSync(ORIGINAL_SRC)) {
        console.error(`❌ Original source not found: ${ORIGINAL_SRC}`);
        console.error('   Make sure the original app is installed and has a frontend/src directory');
        process.exit(1);
    }

    console.log('📋 Copying original source files...');
    await fs.copy(ORIGINAL_SRC, TARGET_SRC);

    // Step 3: Apply overrides
    if (fs.existsSync(CUSTOM_SRC)) {
        console.log('🔀 Applying custom overrides...');
        
        // Find all files in src_override
        const overrideFiles = await glob('**/*', { 
            cwd: CUSTOM_SRC, 
            nodir: true,
            dot: true 
        });

        for (const file of overrideFiles) {
            const srcFile = path.join(CUSTOM_SRC, file);
            const destFile = path.join(TARGET_SRC, file);
            
            // Ensure target directory exists
            await fs.ensureDir(path.dirname(destFile));
            
            // Copy the override file
            await fs.copy(srcFile, destFile);
            console.log(`   ✅ Override: ${file}`);
        }

        console.log(`\n📦 Applied ${overrideFiles.length} override(s)`);
    } else {
        console.log('ℹ️  No src_override directory found, using original source only');
    }

    console.log('✨ Source preparation complete!\n');
}

prepareSrc().catch(err => {
    console.error('❌ Build preparation failed:', err);
    process.exit(1);
});
```

### Step 4: Create vite.config.js

Create `frontend/vite.config.js`:

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import path from 'path';
import { VitePWA } from 'vite-plugin-pwa';

// Read the original app's vite config if needed for reference
// This config is customized for the override build

export default defineConfig({
    plugins: [
        vue(),
        vueJsx(),
        VitePWA({
            registerType: 'autoUpdate',
            workbox: {
                maximumFileSizeToCacheInBytes: 10 * 1024 * 1024, // 10MB
            },
            devOptions: {
                enabled: true
            },
            manifest: {
                name: 'Your Custom App',
                short_name: 'CustomApp',
                theme_color: '#1e40af',
            }
        })
    ],
    
    // IMPORTANT: Output to your custom app's public directory
    build: {
        outDir: path.resolve(__dirname, '../your_custom_app/public/frontend'),
        emptyOutDir: true,
        sourcemap: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    frappe: ['frappe-ui'],
                    vue: ['vue', 'vue-router']
                }
            }
        }
    },
    
    resolve: {
        alias: {
            '@': path.resolve(__dirname, 'src'),
        },
    },
    
    optimizeDeps: {
        include: ['frappe-ui', 'feather-icons', 'showdown', 'vue-router']
    },
    
    // Use the original app's node_modules
    // This allows you to reuse their dependencies
    server: {
        port: 8080,
        proxy: {
            '^/(api|files|assets|socket\\.io)': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            }
        }
    }
});
```

### Step 5: Install Dependencies

```bash
cd frontend

# Install local dependencies
yarn install

# Link to the original app's node_modules
# This is important - it allows you to use their installed packages
ln -sf ../../lms/frontend/node_modules node_modules_linked
```

Or configure your vite config to resolve from the original app's node_modules.

---

## Directory Structure

After setup, your custom app should have this structure:

```
your_custom_app/
├── frontend/
│   ├── src_override/           # YOUR CUSTOMIZATIONS GO HERE
│   │   ├── router.js           # Override router (add new routes)
│   │   ├── components/         # New or modified components
│   │   │   └── CustomBanner.vue
│   │   └── pages/              # New or modified pages
│   │       ├── Home/
│   │       │   └── StudentHome.vue  # Modified page
│   │       └── CustomPage.vue       # New page
│   ├── src/                    # AUTO-GENERATED (do not edit)
│   ├── custom-build.js         # Build script
│   ├── vite.config.js          # Vite configuration
│   └── package.json            # Package configuration
│
├── your_custom_app/
│   ├── public/
│   │   └── frontend/           # BUILD OUTPUT
│   │       ├── index.html
│   │       └── assets/
│   └── www/
│       ├── lms.html            # Entry point override
│       └── lms.py              # Context provider
│
└── pyproject.toml
```

### Important Notes

- **`src_override/`** - This is where you put your customizations
- **`src/`** - This is auto-generated during build. NEVER edit files here directly!
- **`public/frontend/`** - Build output, also auto-generated

---

## The Build Process Explained

### How It Works

1. **`yarn prepare-src`** (runs `custom-build.js`)
   - Deletes the existing `src/` directory
   - Copies the original app's entire `frontend/src/` to your `src/`
   - Copies all files from `src_override/` over the top
   - Files with matching paths get replaced

2. **`yarn build`** (runs Vite)
   - Builds the merged source code
   - Outputs to `your_custom_app/public/frontend/`
   - Uses custom base path: `/assets/your_custom_app/frontend/`

### Build Commands

```bash
# Full build
cd frontend
yarn build

# Development mode with hot reload
yarn dev

# Just prepare source (for debugging)
yarn prepare-src
```

### Memory Considerations

Vue/Vite builds can consume significant memory. If you encounter out-of-memory errors:

```bash
# Increase Node.js memory limit
NODE_OPTIONS="--max-old-space-size=4096" yarn build
```

---

## Overriding Components

### Example: Adding a Banner Component

**Step 1:** Create the component in `src_override/components/`:

```vue
<!-- src_override/components/MembershipBanner.vue -->
<template>
    <div class="membership-banner" v-if="showBanner">
        <div class="banner-content">
            <span v-if="isLoading">Loading...</span>
            <template v-else-if="hasMembership">
                <span class="badge">{{ tierName }}</span>
                <span>Active until {{ expiryDate }}</span>
            </template>
            <template v-else>
                <span>Upgrade to Premium for exclusive content</span>
                <router-link to="/membership" class="btn-upgrade">
                    View Plans
                </router-link>
            </template>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createResource } from 'frappe-ui';

const isLoading = ref(true);
const hasMembership = ref(false);
const tierName = ref('');
const expiryDate = ref('');

const membershipResource = createResource({
    url: 'lms_memberships.api.membership.get_membership_status',
    auto: true,
    onSuccess: (data) => {
        hasMembership.value = data.has_active_membership;
        tierName.value = data.tier_name;
        expiryDate.value = data.end_date;
        isLoading.value = false;
    }
});
</script>
```

**Step 2:** Use the component in an overridden page.

### Example: Modifying an Existing Component

Copy the original component and modify it:

```bash
# First, examine the original
cat ../../lms/frontend/src/components/SomeComponent.vue

# Copy to your override directory, maintaining the same path
cp ../../lms/frontend/src/components/SomeComponent.vue \
   src_override/components/SomeComponent.vue

# Now edit src_override/components/SomeComponent.vue
```

---

## Overriding Pages

### Example: Adding Content to Home Page

**Step 1:** Copy the original page:

```bash
cp ../../lms/frontend/src/pages/Home/StudentHome.vue \
   src_override/pages/Home/StudentHome.vue
```

**Step 2:** Modify the copied file to add your customizations:

```vue
<!-- src_override/pages/Home/StudentHome.vue -->
<template>
    <div class="student-home">
        <!-- ADD: Your custom banner -->
        <MembershipBanner />
        
        <!-- KEEP: Original content below -->
        <div class="container mx-auto">
            <!-- ... existing content ... -->
        </div>
    </div>
</template>

<script setup>
// ADD: Import your custom component
import MembershipBanner from '@/components/MembershipBanner.vue';

// KEEP: All original imports
import { ref, computed, onMounted } from 'vue';
// ... rest of original script ...
</script>
```

---

## Adding New Routes

### Override the Router

**Step 1:** Copy and modify the router:

```bash
cp ../../lms/frontend/src/router.js src_override/router.js
```

**Step 2:** Add your custom routes:

```javascript
// src_override/router.js

import { createRouter, createWebHistory } from 'vue-router';

// KEEP: All original imports
import Home from '@/pages/Home.vue';
import Courses from '@/pages/Courses.vue';
// ... other original imports ...

// ADD: Import your custom pages
import Membership from '@/pages/Membership.vue';

const routes = [
    // KEEP: All original routes
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/courses',
        name: 'Courses',
        component: Courses
    },
    // ... other original routes ...

    // ADD: Your custom routes
    {
        path: '/membership',
        name: 'Membership',
        component: Membership,
        meta: {
            title: 'Membership Plans'
        }
    }
];

const router = createRouter({
    history: createWebHistory('/lms'),
    routes
});

export default router;
```

---

## Serving the Custom Frontend

### Create WWW Override

**Step 1:** Create the HTML entry point at `your_custom_app/www/lms.html`:

```html
{% extends "templates/web.html" %}

{% block page_content %}
<div id="app"></div>
{% endblock %}

{% block base_scripts %}
{% endblock %}

{% block script %}
<script>
    // Make Frappe boot info available
    window.csrf_token = '{{ csrf_token }}';
</script>
{% endblock %}

{% block head_include %}
<!-- Custom meta tags -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ title or "LMS" }}</title>

<!-- Load the custom build -->
{{ include_script('lms_memberships.bundle.frontend') }}
{% endblock %}

{% block style %}
<!-- PWA manifest -->
<link rel="manifest" href="/assets/lms_memberships/frontend/manifest.webmanifest">
{% endblock %}
```

**Step 2:** Create the context provider at `your_custom_app/www/lms.py`:

```python
# your_custom_app/www/lms.py

import frappe

no_cache = 1

def get_context(context):
    """Provide context for the LMS frontend override."""
    csrf_token = frappe.sessions.get_csrf_token()
    context.csrf_token = csrf_token
    
    # Add any custom context
    context.title = "LMS"
    
    return context
```

### How URL Routing Works

Frappe's www routing means:
- `your_custom_app/www/lms.html` → serves at `/lms`
- It takes precedence over the original app's `lms.html`
- The Vue router handles all sub-routes like `/lms/courses`

---

## Development Workflow

### Initial Setup

```bash
# 1. Navigate to your custom app's frontend
cd apps/your_custom_app/frontend

# 2. Install dependencies
yarn install

# 3. Build for the first time
NODE_OPTIONS="--max-old-space-size=4096" yarn build

# 4. Build Frappe assets
cd ../../../
bench build --app your_custom_app

# 5. Restart bench
bench restart
```

### Daily Development

```bash
# Quick iteration cycle
cd apps/your_custom_app/frontend

# Option A: Full rebuild
yarn build && cd ../../../ && bench build --app your_custom_app

# Option B: Development mode with hot reload
yarn dev
# Then access http://localhost:8080 (proxies to Frappe)
```

### After Updating the Original App

When the original app (e.g., LMS) is updated:

```bash
# Pull updates
cd apps/lms
git pull

# Rebuild your overrides
cd ../your_custom_app/frontend
yarn build

# Rebuild assets
cd ../../../
bench build --app your_custom_app
```

---

## Troubleshooting

### Common Issues

#### 1. "Original source not found"

```
❌ Original source not found: /path/to/lms/frontend/src
```

**Solution:** Check that the original app is installed and has a frontend directory:
```bash
ls -la apps/lms/frontend/src
```

#### 2. Out of Memory During Build

```
FATAL ERROR: CALL_AND_RETRY_LAST Allocation failed - JavaScript heap out of memory
```

**Solution:** Increase Node.js memory:
```bash
NODE_OPTIONS="--max-old-space-size=4096" yarn build
```

#### 3. Assets Not Loading

**Symptoms:** Blank page, 404 errors for JS/CSS files

**Solutions:**
1. Check `bench build --app your_custom_app` was run
2. Verify base path in vite.config.js matches: `/assets/your_custom_app/frontend/`
3. Check the HTML template includes the correct bundle

#### 4. Route Not Found

**Symptoms:** Vue router shows 404 for new routes

**Solutions:**
1. Ensure router.js is in src_override/
2. Check the route path and component import
3. Rebuild and refresh

#### 5. Component Not Updating

**Symptoms:** Changes to override files don't appear

**Solutions:**
1. Delete `src/` directory and rebuild
2. Clear browser cache
3. Run `yarn prepare-src` manually to check

### Debug Tips

```bash
# Check what's in the merged src/
ls -la src/

# Compare with original
diff src/router.js ../../lms/frontend/src/router.js

# Check build output
ls -la ../your_custom_app/public/frontend/

# View Frappe asset configuration
cat ../your_custom_app/public/bundle.json
```

---

## Best Practices

### 1. Minimal Overrides

Only override what you need to change. The fewer files you override, the easier it is to merge upstream changes.

### 2. Comment Your Changes

When modifying existing files, clearly mark your additions:

```vue
<template>
    <!-- [CUSTOM] Added membership banner -->
    <MembershipBanner />
    
    <!-- Original content below -->
    <div class="content">
```

```javascript
// [CUSTOM] Import membership component
import MembershipBanner from '@/components/MembershipBanner.vue';

// Original imports
import { ref } from 'vue';
```

### 3. Keep Override Structure Parallel

Match the original app's directory structure exactly:
- Original: `lms/frontend/src/pages/Home/StudentHome.vue`
- Override: `your_app/frontend/src_override/pages/Home/StudentHome.vue`

### 4. Version Control

Add to your `.gitignore`:
```gitignore
# Auto-generated - DO NOT COMMIT
frontend/src/
frontend/node_modules/

# Build output - optionally commit or exclude
# your_custom_app/public/frontend/
```

### 5. Document Dependencies

If your overrides need the original app at a specific version:

```python
# hooks.py
app_include_js = [...]
app_include_css = [...]

# Add dependency (for documentation)
required_apps = ["frappe", "lms>=2.30.0"]
```

### 6. Test After Original App Updates

Create a checklist for when the original app updates:

1. Review changelog for breaking changes
2. Check if overridden files changed significantly
3. Rebuild and test all customizations
4. Update your override files if needed

---

## Examples

### Example 1: Adding a Simple Notification Banner

```vue
<!-- src_override/components/NotificationBanner.vue -->
<template>
    <div class="notification-banner" v-if="message">
        <p>{{ message }}</p>
        <button @click="dismiss">×</button>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { createResource } from 'frappe-ui';

const message = ref('');

const bannerResource = createResource({
    url: 'your_app.api.get_banner_message',
    auto: true,
    onSuccess: (data) => {
        message.value = data.message;
    }
});

function dismiss() {
    message.value = '';
}
</script>

<style scoped>
.notification-banner {
    background: #1e40af;
    color: white;
    padding: 0.75rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
```

### Example 2: Adding a New Page with API Integration

```vue
<!-- src_override/pages/CustomDashboard.vue -->
<template>
    <div class="custom-dashboard">
        <header>
            <h1>Custom Dashboard</h1>
        </header>
        
        <div class="stats-grid" v-if="!loading">
            <div class="stat-card" v-for="stat in stats" :key="stat.label">
                <span class="stat-value">{{ stat.value }}</span>
                <span class="stat-label">{{ stat.label }}</span>
            </div>
        </div>
        
        <LoadingIndicator v-else />
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { createResource } from 'frappe-ui';
import LoadingIndicator from '@/components/LoadingIndicator.vue';

const statsResource = createResource({
    url: 'your_app.api.get_dashboard_stats',
    auto: true
});

const loading = computed(() => statsResource.loading);
const stats = computed(() => statsResource.data || []);
</script>
```

### Example 3: Extending an Existing Page

```vue
<!-- src_override/pages/Courses.vue -->
<!-- Copy of original with custom additions -->
<template>
    <div class="courses-page">
        <!-- [CUSTOM] Premium courses filter -->
        <div class="premium-filter" v-if="hasPremiumAccess">
            <label>
                <input type="checkbox" v-model="showPremiumOnly">
                Show Premium Only
            </label>
        </div>
        
        <!-- Original course grid (keep as-is) -->
        <div class="course-grid">
            <CourseCard 
                v-for="course in filteredCourses" 
                :key="course.name"
                :course="course"
            />
        </div>
    </div>
</template>

<script setup>
// [CUSTOM] Import membership check
import { useMembershipStatus } from '@/composables/useMembershipStatus';

// Original imports
import { ref, computed } from 'vue';
import CourseCard from '@/components/CourseCard.vue';
import { createResource } from 'frappe-ui';

// [CUSTOM] Membership integration
const { hasPremiumAccess } = useMembershipStatus();
const showPremiumOnly = ref(false);

// Original course loading
const coursesResource = createResource({
    url: 'lms.lms.api.get_courses',
    auto: true
});

// [CUSTOM] Enhanced filtering
const filteredCourses = computed(() => {
    const courses = coursesResource.data || [];
    if (showPremiumOnly.value) {
        return courses.filter(c => c.is_premium);
    }
    return courses;
});
</script>
```

---

## Summary

The Vue Override pattern enables powerful customization of Frappe Vue applications while maintaining clean separation from the original codebase. Key points:

1. **Use `src_override/`** for all your customizations
2. **Never edit `src/`** directly - it's auto-generated
3. **Match directory structure** exactly with the original app
4. **Build after every change** using `yarn build`
5. **Run `bench build`** to update Frappe assets
6. **Test thoroughly** after original app updates

This approach scales well from simple component additions to comprehensive application modifications, all while keeping your changes isolated and maintainable.

---

## Additional Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [Frappe UI Components](https://frappeui.com)
- [Vue.js Documentation](https://vuejs.org)
- [Vite Documentation](https://vitejs.dev)
- [crm_override Example](https://github.com/esafwan/crm_override)

---

*Last updated: $(date +%Y-%m-%d)*
*Applicable to: Frappe v14+, Vue 3, Vite*
