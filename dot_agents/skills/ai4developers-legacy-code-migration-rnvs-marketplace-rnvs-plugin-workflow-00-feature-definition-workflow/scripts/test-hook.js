#!/usr/bin/env node
/**
 * Test hook to debug working directory and environment
 */
const fs = require('fs');
const path = require('path');

// Read JSON input from stdin
let inputData = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => inputData += chunk);
process.stdin.on('end', () => {
    const logFile = '/tmp/skill-hook-debug.log';

    const debugInfo = {
        timestamp: new Date().toISOString(),
        cwd: process.cwd(),
        env: {
            CLAUDE_PROJECT_DIR: process.env.CLAUDE_PROJECT_DIR || 'NOT SET',
            CLAUDE_PLUGIN_ROOT: process.env.CLAUDE_PLUGIN_ROOT || 'NOT SET'
        },
        __dirname: __dirname,
        __filename: __filename,
        inputData: inputData.substring(0, 500) // First 500 chars
    };

    fs.appendFileSync(logFile, JSON.stringify(debugInfo, null, 2) + '\n---\n');
    console.log(`[Test Hook] Debug info written to ${logFile}`);
    process.exit(0);
});
