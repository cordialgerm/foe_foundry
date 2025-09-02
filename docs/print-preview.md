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
        
        <monster-statblock 
            src-from-url="true"
            hide-buttons="true"
            print-preview="true"
        ></monster-statblock>
    </div>

    <script type="module">
        // Import the monster-statblock component
        import '/src/components/MonsterStatblock.js';
        
        // Set the base URL for API calls
        window.baseUrl = window.baseUrl || '';
    </script>
</body>
</html>