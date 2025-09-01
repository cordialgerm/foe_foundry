---
title: Print Preview | Foe Foundry
description: Print-friendly monster statblock view
hide:
  - navigation
  - toc
  - backlinks
  - related_monsters
---

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Print Preview - Foe Foundry</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
            background: white;
            color: black;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        @media print {
            body {
                padding: 0;
            }
            .no-print {
                display: none !important;
            }
        }
        
        .print-header {
            text-align: center;
            margin-bottom: 2rem;
            border-bottom: 1px solid #ccc;
            padding-bottom: 1rem;
        }
        
        .print-header h1 {
            margin: 0 0 0.5rem 0;
            font-size: 1.5rem;
        }
        
        .print-header p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="print-header no-print">
            <h1>Print Preview</h1>
            <p>Use your browser's print function (Ctrl+P / Cmd+P) to print this statblock</p>
        </div>
        
        <div id="statblock-container">
            <!-- Statblock will be loaded here -->
        </div>
    </div>

    <script>
        // Parse URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const monsterKey = urlParams.get('monster-key');
        const hpMultiplier = parseFloat(urlParams.get('hp-multiplier')) || 1;
        const damageMultiplier = parseFloat(urlParams.get('damage-multiplier')) || 1;
        const powers = urlParams.get('powers') || '';

        async function loadStatblock() {
            if (!monsterKey) {
                document.getElementById('statblock-container').innerHTML = 
                    '<p style="text-align: center; color: #666;">No monster specified</p>';
                return;
            }

            try {
                const payload = {
                    monster_key: monsterKey,
                    powers: powers ? powers.split(',').map(p => p.trim()).filter(p => p) : [],
                    hp_multiplier: hpMultiplier,
                    damage_multiplier: damageMultiplier
                };

                const baseUrl = window.baseUrl || '';
                const response = await fetch(`${baseUrl}/api/v1/statblocks/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error(`Failed to generate statblock: ${response.statusText}`);
                }

                const result = await response.json();
                const statblockHtml = result.statblock_html;
                
                const container = document.getElementById('statblock-container');
                container.innerHTML = statblockHtml;

                // Add print-preview class to all stat-block elements
                const statBlocks = container.querySelectorAll('.stat-block');
                statBlocks.forEach(block => {
                    block.classList.add('print-preview');
                });

            } catch (error) {
                console.error('Error loading statblock:', error);
                document.getElementById('statblock-container').innerHTML = 
                    `<p style="text-align: center; color: #d32f2f;">Error loading statblock: ${error.message}</p>`;
            }
        }

        // Load statblock when page loads
        document.addEventListener('DOMContentLoaded', loadStatblock);
    </script>
</body>
</html>