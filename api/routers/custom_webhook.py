# api/routers/custom_webhook.py
"""
Custom webhook endpoint that serves a Premium Trial Offer HTML page.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

CUSTOM_WEBHOOK_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Premium Trial Offer</title>

    <!-- Google Fonts Import -->
    <!-- To change font: Visit https://fonts.google.com, select a font, copy the <link> tags, and update font-family in CSS -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">

    <style>
        /* ========================================
           CUSTOMIZATION SECTION
           ======================================== */
        :root {
            /* BACKGROUND COLORS - Safe to customize */
            --modal-background: #ffffff;
            --content-background: #ffffff;

            /* TEXT COLORS - Safe to customize */
            --text-primary: #1a1a1a;
            --text-secondary: #4a4a4a;
            --text-button-primary: #ffffff;
            --text-button-secondary: #6b7280;

            /* SPACING & SIZING - Safe to customize */
            --container-padding: 24px;
            --content-padding: 32px;
            --border-radius: 20px;
            --feature-icon-size: 24px;
            --background-image-height: 280px;

            /* TYPOGRAPHY - Safe to customize */
            /* To change font: Update Google Fonts import above, then change font-family below */
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            --font-size-title: 28px;
            --font-size-subtitle: 16px;
            --font-size-feature: 18px;
            --font-size-button-primary: 16px;
            --font-size-button-secondary: 16px;

            /* BUTTON STYLING - Safe to customize */
            --button-primary-background: #401fa7;
            --button-border-radius: 12px;
            --button-height: 56px;
        }
        /* ========================================
           CORE STYLES - DO NOT MODIFY
           ======================================== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: var(--font-family);
            background: rgba(0, 0, 0, 0.5);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--container-padding);
            overflow: hidden;
        }
        .iam-container {
            width: 100%;
            max-width: 400px;
            background: var(--modal-background);
            border-radius: var(--border-radius);
            position: relative;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .close-button {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 32px;
            height: 32px;
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: #ffffff;
            z-index: 10;
            transition: background-color 0.2s ease;
        }
        .close-button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        .background-image-section {
            width: 100%;
            height: var(--background-image-height);
            background: url('https://img.onesignal.com/i/eb044a1c-9927-4cd6-a2e0-fa08c5d6c585/lctD4avNS72YhUTGwUEt_promotional-in-app-illustration-3.png') center center;
            background-size: cover;
            background-repeat: no-repeat;
            position: relative;
        }
        .content {
            padding: var(--content-padding);
            background: var(--content-background);
            border-radius: var(--border-radius) var(--border-radius) 0 0;
            margin-top: -20px;
            position: relative;
            z-index: 2;
        }
        .title {
            font-size: var(--font-size-title);
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 16px;
            line-height: 1.2;
        }
        .subtitle {
            font-size: var(--font-size-subtitle);
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 32px;
        }
        .features-list {
            margin-bottom: 32px;
        }
        .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }
        .feature-item:last-child {
            margin-bottom: 0;
        }
        .feature-icon {
            width: var(--feature-icon-size);
            height: var(--feature-icon-size);
            margin-right: 16px;
            flex-shrink: 0;
        }
        .feature-text {
            font-size: var(--font-size-feature);
            font-weight: 500;
            color: var(--text-primary);
            line-height: 1.3;
        }
        .buttons-container {
            display: flex;
            flex-direction: column;
            gap: 16px;
            align-items: center;
        }
        .primary-button {
            width: 100%;
            height: var(--button-height);
            background: var(--button-primary-background);
            color: var(--text-button-primary);
            border: none;
            border-radius: var(--button-border-radius);
            font-size: var(--font-size-button-primary);
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s ease;
            font-family: var(--font-family);
        }
        .primary-button:hover {
            opacity: 0.9;
        }
        .primary-button:active {
            transform: scale(0.98);
        }
        .secondary-button {
            background: none;
            border: none;
            color: var(--text-button-secondary);
            font-size: var(--font-size-button-secondary);
            font-weight: 500;
            cursor: pointer;
            transition: color 0.2s ease;
            font-family: var(--font-family);
            text-decoration: underline;
        }
        .secondary-button:hover {
            color: var(--text-primary);
        }
        /* Mobile optimizations */
        @media (max-width: 480px) {
            :root {
                --container-padding: 16px;
                --content-padding: 24px;
                --font-size-title: 24px;
                --font-size-subtitle: 15px;
                --font-size-feature: 16px;
                --background-image-height: 240px;
            }
            .close-button {
                top: 16px;
                right: 16px;
                width: 28px;
                height: 28px;
                font-size: 16px;
                color: #5d6974
            }
            .content {
                margin-top: -15px;
            }
        }
    </style>
</head>
<body>
    <div class="iam-container">
        <!-- Close Button -->
        <button class="close-button" data-onesignal-unique-label="close-button">\u00d7</button>

        <!-- Background Image Section -->
        <div class="background-image-section"></div>

        <!-- Content Section -->
        <div class="content">
            <!-- Customize title below -->
            <h1 class="title">How about another free month of Premium on us?</h1>
            <p class="subtitle">Get more time to take advantage of all your Premium member benefits:</p>

            <!-- Features List - Safe to customize text and add/remove items -->
            <div class="features-list">
                <!-- Feature 1 - Safe to customize text -->
                <div class="feature-item">
                    <img src="https://img.onesignal.com/i/422a2683-dbc7-4ea2-8280-3a578a64c3b1/fnA45rbPShSKBp3AhSJi_Frame.png"
                         alt="Star" class="feature-icon">
                    <span class="feature-text">Ad-free listening</span>
                </div>

                <!-- Feature 2 - Safe to customize text -->
                <div class="feature-item">
                    <img src="https://img.onesignal.com/i/422a2683-dbc7-4ea2-8280-3a578a64c3b1/fnA45rbPShSKBp3AhSJi_Frame.png"
                         alt="Star" class="feature-icon">
                    <span class="feature-text">Early access to new features</span>
                </div>

                <!-- Feature 3 - Safe to customize text -->
                <div class="feature-item">
                    <img src="https://img.onesignal.com/i/422a2683-dbc7-4ea2-8280-3a578a64c3b1/fnA45rbPShSKBp3AhSJi_Frame.png"
                         alt="Star" class="feature-icon">
                    <span class="feature-text">Community access</span>
                </div>
            </div>

            <!-- Action Buttons Container -->
            <div class="buttons-container">
                <!-- Primary Button - Safe to customize text and URL -->
                <!-- Note: This button tags users as interested in the trial offer and redirects to signup -->
                <button class="primary-button" data-onesignal-unique-label="accept-trial-button">Yes, I'll take a free month</button>

                <!-- Secondary Button - Safe to customize text and URL -->
                <!-- Note: This button tags users as NOT interested in the trial and redirects to cancellation/account page -->
                <button class="secondary-button" data-onesignal-unique-label="decline-trial-button">No thanks, cancel membership</button>
            </div>
        </div>
    </div>
    <!-- ========================================
         ONESIGNAL API IMPLEMENTATION
         ======================================== -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Close button handler - Simple close with no user tagging
            const closeButton = document.querySelector('[data-onesignal-unique-label="close-button"]');
            if (closeButton) {
                closeButton.addEventListener('click', function(e) {
                    OneSignalIamApi.close(e);
                });
            }

            // Accept trial button handler
            // This tracks users who are INTERESTED in the free trial offer
            // Replace the URL below with your actual trial signup/redemption URL
            const acceptButton = document.querySelector('[data-onesignal-unique-label="accept-trial-button"]');
            if (acceptButton) {
                acceptButton.addEventListener('click', function(e) {
                    // Tag user as interested in trial offer - useful for follow-up campaigns
                    OneSignalIamApi.tagUser(e, { "trial_interest": "true" });

                    // Redirect to trial signup page - Replace with your actual signup URL
                    OneSignalIamApi.openUrl(e, 'https://www.onesignal.com'); // Replace with your trial signup URL

                    // Close the in-app message
                    OneSignalIamApi.close(e);
                });
            }

            // Decline trial button handler
            // This tracks users who are NOT interested in the free trial offer
            // Replace the URL below with your actual cancellation/account management URL
            const declineButton = document.querySelector('[data-onesignal-unique-label="decline-trial-button"]');
            if (declineButton) {
                declineButton.addEventListener('click', function(e) {
                    // Tag user as NOT interested in trial offer - useful to avoid showing similar offers
                    OneSignalIamApi.tagUser(e, { "trial_interest": "false" });

                    // Redirect to cancellation or account page - Replace with your actual cancellation URL
                    OneSignalIamApi.openUrl(e, 'https://www.onesignal.com'); // Replace with your cancellation/account URL

                    // Close the in-app message
                    OneSignalIamApi.close(e);
                });
            }
        });
    </script>
</body>
</html>"""


@router.get("/custom_webhook", response_class=HTMLResponse)
async def custom_webhook():
    """Serves the Premium Trial Offer HTML page."""
    return CUSTOM_WEBHOOK_HTML
