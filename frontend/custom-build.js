import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const lmsAppPath = path.resolve(__dirname, '../../lms/frontend');
const overrideSrcPath = path.resolve(__dirname, './src');
const overrideFilesPath = path.resolve(__dirname, './src_override');

console.log('==========================================');
console.log('LMS Memberships - Frontend Override Build');
console.log('==========================================');

// Step 1: Copy original LMS frontend src
console.log('\n[1/2] Copying original LMS frontend src...');
if (fs.existsSync(overrideSrcPath)) {
    execSync(`rm -rf "${overrideSrcPath}"`);
}
execSync(`cp -r "${path.join(lmsAppPath, 'src')}" "${overrideSrcPath}"`);
console.log('      ✓ Copied LMS src to ./src');

// Step 2: Apply our overrides
console.log('\n[2/2] Applying lms_memberships overrides...');
execSync(`cp -r "${overrideFilesPath}/"* "${overrideSrcPath}/"`);
console.log('      ✓ Applied overrides from ./src_override');

console.log('\n==========================================');
console.log('Build preparation complete!');
console.log('==========================================\n');
