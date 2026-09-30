"""
VoiceShield AI - Comprehensive Academic Scam & Social Engineering Dataset Generator
Covers 14 realistic categories including English, Hindi, and Hinglish examples.
Generates balanced training, validation, and test splits with explicit intent,
manipulation cues, urgency, and sensitive data requests.
"""

import json
import os
import random
import pandas as pd

CATEGORIES = [
    "Banking Scam",
    "OTP Scam",
    "Phishing",
    "Investment Scam",
    "Job Scam",
    "Delivery Scam",
    "Fake Support",
    "Impersonation",
    "Payment Scam",
    "Romance/Social Engineering",
    "Prize/Reward Scam",
    "Account Verification Scam",
    "Credential Theft",
    "Legitimate / Safe"
]

DATASET_RECORDS = [
    # --- 1. Banking Scam ---
    {
        "text": "URGENT NOTICE: Your State Bank savings account has been temporarily locked due to irregular transactions. Click http://sbi-secure-update.com to verify your PAN immediately.",
        "category": "Banking Scam",
        "intent": "Account Suspension",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Fear", "Authority Impersonation", "Account Suspension Pressure"],
        "sensitive_requested": ["PAN", "Bank Details"],
        "language": "en"
    },
    {
        "text": "Dear customer, your HDFC bank debit card will expire in 24 hours. Update KYC documents immediately at http://hdfc-kyc-portal.net to avoid service interruption.",
        "category": "Banking Scam",
        "intent": "Account Verification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Fear", "Time Pressure", "Authority Impersonation"],
        "sensitive_requested": ["KYC Documents", "Debit Card"],
        "language": "en"
    },
    {
        "text": "Aapka ICICI bank account achanak freeze kar diya gaya hai. Turant diye gaye link par click karein aur account unlock karwayein: http://icici-verify-now.cc",
        "category": "Banking Scam",
        "intent": "Account Suspension",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Fear", "Account Suspension Pressure"],
        "sensitive_requested": ["Bank Details"],
        "language": "hinglish"
    },
    {
        "text": "Bank alert: An unauthorized debit of Rs 48,500 was initiated from your account. If this was not you, call our security helpline immediately at +91-9821098231 to block payment.",
        "category": "Banking Scam",
        "intent": "Threat",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Fear", "Financial Pressure"],
        "sensitive_requested": ["Phone Contact", "Card Number"],
        "language": "en"
    },
    {
        "text": "प्रिय ग्राहक, आपका बैंक खाता आधार से लिंक न होने के कारण निष्क्रिय कर दिया गया है। 2 घंटे में अपडेट करें वरना पेनल्टी लगेगी।",
        "category": "Banking Scam",
        "intent": "Account Suspension",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Fear", "Financial Pressure"],
        "sensitive_requested": ["Aadhaar", "Bank Details"],
        "language": "hi"
    },
    {
        "text": "Axis Bank notification: Your netbanking profile password has expired. Re-authenticate your account credentials here: http://axis-online-secure.org",
        "category": "Banking Scam",
        "intent": "Account Verification",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Authority Impersonation", "Urgency"],
        "sensitive_requested": ["Password", "Login Credentials"],
        "language": "en"
    },

    # --- 2. OTP Scam ---
    {
        "text": "Your one-time passcode for transaction of INR 12,499 is 849201. If you did not authorize this, share this code with our fraud desk officer on call immediately.",
        "category": "OTP Scam",
        "intent": "Request OTP",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Urgency", "Fear", "Authority Impersonation"],
        "sensitive_requested": ["OTP"],
        "language": "en"
    },
    {
        "text": "Sir aapke mobile par abhi ek 6-digit OTP aaya hoga, jaldi bataiye taaki aapka telecom SIM card block hone se bach sake.",
        "category": "OTP Scam",
        "intent": "Request OTP",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Urgency", "Fear", "Authority Impersonation"],
        "sensitive_requested": ["OTP"],
        "language": "hinglish"
    },
    {
        "text": "Google verification code: 391-402. Do not share. If requested by support staff to confirm identity, send reply SMS with this code.",
        "category": "OTP Scam",
        "intent": "Request OTP",
        "urgency": "HIGH",
        "manipulation_techniques": ["Trust Exploitation", "Authority Impersonation"],
        "sensitive_requested": ["OTP", "Verification Code"],
        "language": "en"
    },
    {
        "text": "Electric bill pending alert: Power supply will be disconnected at 9:30 PM tonight. Share the verification SMS code to cancel disconnection.",
        "category": "OTP Scam",
        "intent": "Request OTP",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Urgency", "Threat", "Time Pressure"],
        "sensitive_requested": ["OTP"],
        "language": "en"
    },
    {
        "text": "Aapka Paytm wallet KYC expire ho gaya hai. Abhi bheja gaya OTP share karein taaki hum turant KYC verify kar sakein.",
        "category": "OTP Scam",
        "intent": "Request OTP",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Authority Impersonation"],
        "sensitive_requested": ["OTP", "KYC Documents"],
        "language": "hinglish"
    },

    # --- 3. Phishing ---
    {
        "text": "Security Alert: Someone attempted to access your Microsoft 365 Outlook account from Russia. Review and confirm your login password here: http://login-microsoft-secure.me",
        "category": "Phishing",
        "intent": "Link Click Request",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Urgency", "Authority Impersonation"],
        "sensitive_requested": ["Password", "Login Credentials"],
        "language": "en"
    },
    {
        "text": "Netflix Membership: Your billing payment failed. Update credit card details now to keep your subscription active: http://netflix-billing-resolve.xyz",
        "category": "Phishing",
        "intent": "Link Click Request",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Scarcity", "Curiosity"],
        "sensitive_requested": ["Credit Card", "CVV"],
        "language": "en"
    },
    {
        "text": "Aapka income tax refund of Rs 24,750 approve ho chuka hai. Is link par click karke details verify karein aur turant payout paayein: http://incometax-refund-gov.in.co",
        "category": "Phishing",
        "intent": "Refund Request",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Reward/Greed", "Authority Impersonation"],
        "sensitive_requested": ["Bank Details", "PAN"],
        "language": "hinglish"
    },
    {
        "text": "Instagram Copyright Violation: Your post violated community copyright. You have 24 hours to appeal before permanent account deletion: http://meta-copyright-appeal.cc",
        "category": "Phishing",
        "intent": "Threat",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Time Pressure", "Threat"],
        "sensitive_requested": ["Password"],
        "language": "en"
    },
    {
        "text": "IRS tax notification: You have unpaid tax penalties. Immediate legal action will be initiated. Click to view legal document: http://irs-case-review.top",
        "category": "Phishing",
        "intent": "Threat",
        "urgency": "HIGH",
        "manipulation_techniques": ["Threat", "Fear", "Authority Impersonation"],
        "sensitive_requested": ["Identity Info"],
        "language": "en"
    },

    # --- 4. Investment Scam ---
    {
        "text": "Guaranteed 400% returns in 48 hours with automated crypto arbitrage! Join our VIP Telegram channel today. Minimum deposit only $250.",
        "category": "Investment Scam",
        "intent": "Investment Request",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Reward/Greed", "Scarcity", "Trust Exploitation"],
        "sensitive_requested": ["Payment", "Crypto Wallet"],
        "language": "en"
    },
    {
        "text": "Bhai mere pass insider trading stock tips hain. Roj 20,000 kamayein bina risk ke. WhatsApp par contact karo aur aaj hi start karo investment.",
        "category": "Investment Scam",
        "intent": "Investment Request",
        "urgency": "LOW",
        "manipulation_techniques": ["Reward/Greed", "Trust Exploitation"],
        "sensitive_requested": ["Payment"],
        "language": "hinglish"
    },
    {
        "text": "Exclusive Pre-IPO allocation for SpaceX shares reserved for select accredited investors. Deposit funds within 3 hours to lock in tier-1 price.",
        "category": "Investment Scam",
        "intent": "Investment Request",
        "urgency": "HIGH",
        "manipulation_techniques": ["Scarcity", "Reward/Greed", "Time Pressure"],
        "sensitive_requested": ["Payment", "Bank Details"],
        "language": "en"
    },
    {
        "text": "Forex signal bot with 99.4% win rate. Double your capital every week. Limited to the first 50 participants who deposit $500 today.",
        "category": "Investment Scam",
        "intent": "Investment Request",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Scarcity", "Reward/Greed"],
        "sensitive_requested": ["Payment"],
        "language": "en"
    },
    {
        "text": "घर बैठे शेयर बाजार में निवेश करें और रोजाना ₹5000 कमाएं। 100% सुरक्षित और सरकार द्वारा प्रमाणित गारंटी।",
        "category": "Investment Scam",
        "intent": "Investment Request",
        "urgency": "LOW",
        "manipulation_techniques": ["Reward/Greed", "Trust Exploitation"],
        "sensitive_requested": ["Payment"],
        "language": "hi"
    },

    # --- 5. Job Scam ---
    {
        "text": "Amazon Part-Time Hiring: Earn INR 3,000 to 8,000 daily by simply rating products from home. No prior experience needed. Contact WhatsApp: +91-9988776655.",
        "category": "Job Scam",
        "intent": "Job Offer",
        "urgency": "LOW",
        "manipulation_techniques": ["Reward/Greed", "Curiosity", "Authority Impersonation"],
        "sensitive_requested": ["Phone Contact"],
        "language": "en"
    },
    {
        "text": "Congratulations! You are shortlisted for Google India remote data entry specialist. Monthly salary Rs 85,000. Pay Rs 1,499 registration fee to receive offer letter.",
        "category": "Job Scam",
        "intent": "Request Payment",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Authority Impersonation", "Reward/Greed", "Financial Pressure"],
        "sensitive_requested": ["Registration Fee", "Personal Information"],
        "language": "en"
    },
    {
        "text": "Aapka resume select hua hai Canadian work permit job ke liye. Salary $4,500 CAD/month. Visa processing fee turant transfer karein.",
        "category": "Job Scam",
        "intent": "Request Payment",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Reward/Greed", "Authority Impersonation"],
        "sensitive_requested": ["Payment", "Passport Details"],
        "language": "hinglish"
    },
    {
        "text": "YouTube video like & subscribe job. Earn Rs 50 per like. Register now with Telegram @JobOfficer77 and submit initial deposit of Rs 2000 for VIP tasks.",
        "category": "Job Scam",
        "intent": "Job Offer",
        "urgency": "LOW",
        "manipulation_techniques": ["Reward/Greed", "Trust Exploitation"],
        "sensitive_requested": ["Payment", "Bank Details"],
        "language": "en"
    },

    # --- 6. Delivery Scam ---
    {
        "text": "FedEx: Your package delivery has been stopped due to incomplete street address. Pay $1.99 redelivery fee at http://fedex-parcel-redeliver.info within 12 hours.",
        "category": "Delivery Scam",
        "intent": "Delivery Notification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Urgency", "Time Pressure", "Authority Impersonation"],
        "sensitive_requested": ["Credit Card", "Address Details"],
        "language": "en"
    },
    {
        "text": "India Post alert: Your consignment number IN93821034 is on hold at customs. Update address and pay clearance fee: http://indiapost-customs-clear.site",
        "category": "Delivery Scam",
        "intent": "Delivery Notification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Urgency"],
        "sensitive_requested": ["Payment", "Address Details"],
        "language": "en"
    },
    {
        "text": "Aapka parcel BlueDart warehouse mein ruka hua hai kyunki pin code galat tha. Turant Rs 15 ka charge dekar re-schedule karein: http://bluedart-trace.online",
        "category": "Delivery Scam",
        "intent": "Delivery Notification",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Urgency", "Authority Impersonation"],
        "sensitive_requested": ["Payment", "Card Number"],
        "language": "hinglish"
    },
    {
        "text": "DHL Express: Delivery attempted but recipient was unavailable. Click here to confirm identity and pay customs VAT: http://dhl-express-dispatch.top",
        "category": "Delivery Scam",
        "intent": "Delivery Notification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Urgency"],
        "sensitive_requested": ["Payment", "Personal Information"],
        "language": "en"
    },

    # --- 7. Fake Support ---
    {
        "text": "Windows Technical Support: Severe Trojan malware detected on your computer. Your files will be encrypted. Call Microsoft certified engineers right now at 1-800-419-0291.",
        "category": "Fake Support",
        "intent": "Threat",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Fear", "Urgency", "Authority Impersonation"],
        "sensitive_requested": ["Remote Access", "Phone Call"],
        "language": "en"
    },
    {
        "text": "Apple Support Notice: Your iCloud account is locked due to unauthorized access attempts. Verify your Apple ID password and security questions to restore access.",
        "category": "Fake Support",
        "intent": "Account Verification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Fear"],
        "sensitive_requested": ["Apple ID", "Password", "Security Questions"],
        "language": "en"
    },
    {
        "text": "Sir main WhatsApp customer desk se bol raha hoon, aapke account par multiple report aayi hain. AnyDesk install kijiye taaki main check kar sakun.",
        "category": "Fake Support",
        "intent": "Customer Support",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Fear", "Trust Exploitation"],
        "sensitive_requested": ["Remote Access", "AnyDesk"],
        "language": "hinglish"
    },
    {
        "text": "Meta Support: We received reports of spam from your business page. Connect with live chat support at http://meta-business-appeal.net to prevent page deletion.",
        "category": "Fake Support",
        "intent": "Customer Support",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Authority Impersonation", "Threat"],
        "sensitive_requested": ["Login Credentials"],
        "language": "en"
    },

    # --- 8. Impersonation ---
    {
        "text": "Hi Dad, I dropped my phone in water and this is my new temporary number. I urgently need $850 to pay my rent before 5 PM. Can you transfer it via Zelle right now?",
        "category": "Impersonation",
        "intent": "Request Payment",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Emotional Pressure", "Urgency", "Trust Exploitation", "Time Pressure"],
        "sensitive_requested": ["Payment", "Transfer"],
        "language": "en"
    },
    {
        "text": "Hello, this is Sundar Pichai, CEO of Google. I am on an urgent international trip and need you to purchase 5 Apple gift cards of $100 each for a client presentation.",
        "category": "Impersonation",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Urgency", "Secrecy"],
        "sensitive_requested": ["Gift Cards", "Payment"],
        "language": "en"
    },
    {
        "text": "Bhai main tere office ka manager bol raha hoon. Ek emergency client payment karni hai UPI se. Main tujhe shaam ko cash de dunga, jaldi ₹15,000 bhej de.",
        "category": "Impersonation",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Emotional Pressure", "Urgency"],
        "sensitive_requested": ["UPI Payment"],
        "language": "hinglish"
    },
    {
        "text": "This is Officer Vikram Sharma from Delhi Police Cyber Crime Cell. A warrant has been issued in your name for money laundering. Contact immediately on Telegram.",
        "category": "Impersonation",
        "intent": "Threat",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Authority Impersonation", "Fear", "Threat"],
        "sensitive_requested": ["Personal Info", "Contact"],
        "language": "en"
    },

    # --- 9. Payment Scam ---
    {
        "text": "Scan this Google Pay QR code to receive Rs 15,000 cashback directly in your bank account. Enter your 6-digit UPI PIN when prompted to confirm deposit.",
        "category": "Payment Scam",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Reward/Greed", "Trust Exploitation"],
        "sensitive_requested": ["UPI PIN"],
        "language": "en"
    },
    {
        "text": "Overpayment notice: We accidentally sent you $1,200 instead of $120 for your eBay listing. Please wire back the $1,080 difference via Western Union immediately.",
        "category": "Payment Scam",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Emotional Pressure", "Financial Pressure", "Urgency"],
        "sensitive_requested": ["Wire Transfer", "Payment"],
        "language": "en"
    },
    {
        "text": "Aapke PhonePe par cashback offer aaya hai. Claim karne ke liye QR code scan karein aur apna secret MPIN enter karein.",
        "category": "Payment Scam",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Reward/Greed", "Trust Exploitation"],
        "sensitive_requested": ["MPIN", "UPI PIN"],
        "language": "hinglish"
    },
    {
        "text": "QuickBooks billing: An invoice of $949.00 has been auto-charged to your bank. To dispute this charge and request an instant refund, call +1-888-294-1182.",
        "category": "Payment Scam",
        "intent": "Refund Request",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Financial Pressure", "Urgency"],
        "sensitive_requested": ["Bank Details", "Remote Access"],
        "language": "en"
    },

    # --- 10. Romance/Social Engineering ---
    {
        "text": "My dearest love, I have arrived in London but my customs baggage is held with gold jewelry gifts for you. Please transfer £1,400 to the customs clearing officer so I can reach you.",
        "category": "Romance/Social Engineering",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Emotional Pressure", "Trust Exploitation", "Secrecy"],
        "sensitive_requested": ["Wire Transfer", "Payment"],
        "language": "en"
    },
    {
        "text": "I feel so connected to you after our conversations. My military deployment in Syria is dangerous and my commander will only grant medical leave if you pay the $2,000 leave clearance fee.",
        "category": "Romance/Social Engineering",
        "intent": "Request Payment",
        "urgency": "HIGH",
        "manipulation_techniques": ["Emotional Pressure", "Trust Exploitation", "Urgency"],
        "sensitive_requested": ["Payment"],
        "language": "en"
    },
    {
        "text": "Sweetheart, don't tell anyone about our investment deal, it is just between you and me. Transfer your savings to this private crypto wallet so our future is secure.",
        "category": "Romance/Social Engineering",
        "intent": "Investment Request",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Secrecy", "Emotional Pressure", "Trust Exploitation"],
        "sensitive_requested": ["Crypto Wallet", "Payment"],
        "language": "en"
    },

    # --- 11. Prize/Reward Scam ---
    {
        "text": "CONGRATULATIONS! Your mobile number was chosen as the lucky winner of a brand new BMW 5 Series and 25 Lakhs cash in Kaun Banega Crorepati lucky draw! Call KBC manager.",
        "category": "Prize/Reward Scam",
        "intent": "Prize/Reward",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Reward/Greed", "Authority Impersonation"],
        "sensitive_requested": ["Registration Fee", "Personal Information"],
        "language": "en"
    },
    {
        "text": "Aapne jeeta hai Flipkart Big Billion Days ka 1st Prize iPhone 15 Pro Max! Sirf shipping charge ₹499 pay karke abhi claim karein: http://flipkart-winner-claim.co",
        "category": "Prize/Reward Scam",
        "intent": "Prize/Reward",
        "urgency": "HIGH",
        "manipulation_techniques": ["Reward/Greed", "Scarcity", "Time Pressure"],
        "sensitive_requested": ["Payment", "Card Details"],
        "language": "hinglish"
    },
    {
        "text": "You have an unclaimed reward balance of $4,500 waiting in your shopper account. Click here to verify identity and transfer cash to PayPal before midnight.",
        "category": "Prize/Reward Scam",
        "intent": "Prize/Reward",
        "urgency": "HIGH",
        "manipulation_techniques": ["Reward/Greed", "Time Pressure", "Scarcity"],
        "sensitive_requested": ["PayPal", "Bank Details"],
        "language": "en"
    },
    {
        "text": "बधाई हो! आपको रिलायंस जियो की तरफ से 1 वर्ष का 5G फ्री रिचार्ज मिला है। तुरंत एक्टिवेट करने के लिए लिंक खोलें और 5 दोस्तों को शेयर करें।",
        "category": "Prize/Reward Scam",
        "intent": "Prize/Reward",
        "urgency": "MEDIUM",
        "manipulation_techniques": ["Reward/Greed", "Social Pressure"],
        "sensitive_requested": ["Contacts", "Personal Details"],
        "language": "hi"
    },

    # --- 12. Account Verification Scam ---
    {
        "text": "SBI Alert: Your NetBanking account will be terminated unless PAN verification is completed within 30 minutes. Visit http://onlinesbi-pan-validate.info to upload details.",
        "category": "Account Verification Scam",
        "intent": "Account Verification",
        "urgency": "CRITICAL",
        "manipulation_techniques": ["Urgency", "Time Pressure", "Fear", "Account Suspension Pressure"],
        "sensitive_requested": ["PAN", "NetBanking Credentials"],
        "language": "en"
    },
    {
        "text": "WhatsApp compliance team: Your phone number is scheduled for deactivation due to security compliance rules. Verify your 6-digit registration PIN to keep using WhatsApp.",
        "category": "Account Verification Scam",
        "intent": "Account Verification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Authority Impersonation", "Fear", "Urgency"],
        "sensitive_requested": ["PIN", "Verification Code"],
        "language": "en"
    },
    {
        "text": "Paytm KYC verification pending: Dear user, complete your Aadhaar biometric re-verification by clicking http://paytm-kyc-desk.cc to prevent wallet freeze.",
        "category": "Account Verification Scam",
        "intent": "Account Verification",
        "urgency": "HIGH",
        "manipulation_techniques": ["Account Suspension Pressure", "Authority Impersonation"],
        "sensitive_requested": ["Aadhaar", "KYC Documents"],
        "language": "en"
    },

    # --- 13. Credential Theft ---
    {
        "text": "University IT Services: Your campus email quota is 99% full. All incoming emails are held. Validate your username and campus password here: http://edu-portal-auth.online",
        "category": "Credential Theft",
        "intent": "Credential Harvesting",
        "urgency": "HIGH",
        "manipulation_techniques": ["Scarcity", "Urgency", "Authority Impersonation"],
        "sensitive_requested": ["Username", "Password"],
        "language": "en"
    },
    {
        "text": "GitHub Security: We detected a secret token leak in your repository. Sign in immediately to rotate your Personal Access Token and SSH key credentials: http://github-auth-token.xyz",
        "category": "Credential Theft",
        "intent": "Credential Harvesting",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Urgency", "Authority Impersonation"],
        "sensitive_requested": ["Password", "Access Token", "SSH Key"],
        "language": "en"
    },
    {
        "text": "Aapka Facebook password reset request initiate kiya gaya hai. Agar aapne yeh nahi kiya toh turant apna current password aur phone number enter karke secure karein.",
        "category": "Credential Theft",
        "intent": "Credential Harvesting",
        "urgency": "HIGH",
        "manipulation_techniques": ["Fear", "Urgency"],
        "sensitive_requested": ["Current Password", "Phone Number"],
        "language": "hinglish"
    },

    # --- 14. Legitimate / Safe ---
    {
        "text": "Hi Team, please find attached the minutes of our quarterly project review meeting. Let me know if you have any questions before our Friday standup.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "Your Swiggy order from Biryani Blues has been picked up by delivery partner Ramesh. Track live delivery on your official Swiggy mobile application.",
        "category": "Legitimate / Safe",
        "intent": "Delivery Notification",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "Dear customer, your electricity bill of Rs 1,420 for month of August is generated. Last date to pay is 15th October via official electricity board portal or app.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "Haan bhai, kal shaam ko 6 baje coffee shop par milte hain college project discussion ke liye. Notes le aana saath mein.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "hinglish"
    },
    {
        "text": "Reminder: Your dental appointment with Dr. Mehta is confirmed for tomorrow at 4:30 PM. Please arrive 10 minutes prior.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "नमस्ते राहुल, कल की क्लास की टाइमिंग सुबह 9 बजे कर दी गई है। कृपया समय पर लैब में उपस्थित रहें।",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "hi"
    },
    {
        "text": "Your Uber ride with driver Suresh is arriving in 3 minutes in a White Swift Dzire (MH 02 CE 4910). Have a pleasant trip.",
        "category": "Legitimate / Safe",
        "intent": "Delivery Notification",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "Hi Mom, reaching home by 8 PM today after college. Don't worry about dinner, I had snacks with friends.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    },
    {
        "text": "Your monthly credit card e-statement for statement period ending 20th Sep is ready. Total amount due: INR 5,230. Minimum due: INR 500.",
        "category": "Legitimate / Safe",
        "intent": "Legitimate Inquiry",
        "urgency": "LOW",
        "manipulation_techniques": [],
        "sensitive_requested": [],
        "language": "en"
    }
]

# Academic expansion variations to produce a robust dataset of 280+ diverse samples
def generate_expanded_dataset():
    records = list(DATASET_RECORDS)
    
    variations = [
        # Banking variations
        ("ALERT: {bank} account #{acc} flagged for suspicious international debit of ${amt}. Verify at {link} within {time} hrs.", "Banking Scam", "Account Suspension", "HIGH", ["Urgency", "Fear", "Authority Impersonation"], ["Bank Details", "Password"], "en"),
        ("Dear customer, your {bank} netbanking will be suspended due to non-KYC submission. Click {link} to update Aadhaar/PAN immediately.", "Banking Scam", "Account Verification", "HIGH", ["Urgency", "Account Suspension Pressure", "Authority Impersonation"], ["PAN", "Aadhaar"], "en"),
        ("Aapka {bank} account block hone wala hai. Turant diye gaye link {link} par OTP aur debit card PIN enter karke unblock karein.", "Banking Scam", "Account Suspension", "CRITICAL", ["Urgency", "Fear", "Account Suspension Pressure"], ["OTP", "PIN", "Debit Card"], "hinglish"),
        ("Bank Notice: Tax deduction penalty of Rs {amt} applied to your account. Visit {link} to contest and receive waiver.", "Banking Scam", "Threat", "HIGH", ["Fear", "Financial Pressure"], ["Bank Details"], "en"),
        
        # OTP variations
        ("Do not share OTP with anyone. Your OTP to debit Rs {amt} on {merchant} is {otp}. If not done by you call customer care at {phone}.", "OTP Scam", "Request OTP", "CRITICAL", ["Urgency", "Fear", "Authority Impersonation"], ["OTP"], "en"),
        ("Sir verification code {otp} aaya hoga aapke number pe, jaldi boliyega system update ho raha hai 2 minute mein band ho jayega.", "OTP Scam", "Request OTP", "CRITICAL", ["Urgency", "Time Pressure", "Authority Impersonation"], ["OTP"], "hinglish"),
        ("Delivery parcel OTP: Use code {otp} to accept package. Forward this code to agent on {phone} if not at home.", "OTP Scam", "Request OTP", "HIGH", ["Urgency", "Trust Exploitation"], ["OTP"], "en"),
        
        # Phishing variations
        ("Security Notice: Unusual sign-in from unknown device on your {service} account. Change password now: {link}", "Phishing", "Link Click Request", "HIGH", ["Fear", "Urgency"], ["Password"], "en"),
        ("Aapka {service} account verify nahi hua hai, is link par login karein nahi toh account hamesha ke liye delete ho jayega: {link}", "Phishing", "Threat", "HIGH", ["Fear", "Account Suspension Pressure"], ["Login Credentials"], "hinglish"),
        ("{service} Billing: Your payment method was declined. Update card info immediately to avoid cancellation: {link}", "Phishing", "Link Click Request", "HIGH", ["Urgency", "Scarcity"], ["Credit Card", "CVV"], "en"),
        
        # Investment variations
        ("Invest Rs {amt} today in AI cloud mining and withdraw Rs {ret} guaranteed by tomorrow morning. Zero risk 100% legal. Join {link}", "Investment Scam", "Investment Request", "LOW", ["Reward/Greed", "Trust Exploitation"], ["Payment"], "en"),
        ("Crypto arbitrage bot: Earn 15% daily interest on USDT staking. Regulated and certified. Deposit now to receive 50 USDT signup bonus.", "Investment Scam", "Investment Request", "LOW", ["Reward/Greed", "Scarcity"], ["Crypto Wallet", "Payment"], "en"),
        ("Bhai yeh new crypto token launch ho raha hai, 100x pakka hai. Abhi {amt} invest karoge toh 1 week mein ameer ban jaoge.", "Investment Scam", "Investment Request", "LOW", ["Reward/Greed", "Trust Exploitation"], ["Payment"], "hinglish"),
        
        # Job variations
        ("Earn Rs 2000-5000 per day by reviewing Google Maps hotels and YouTube channels. No skills needed. WhatsApp your resume to {phone}.", "Job Scam", "Job Offer", "LOW", ["Reward/Greed", "Curiosity"], ["Phone Contact"], "en"),
        ("Shortlisted for Flipkart warehouse supervisor role. Monthly salary Rs 42,000 + free hostel. Pay Rs 850 uniform and badge charges to confirm joining.", "Job Scam", "Request Payment", "MEDIUM", ["Authority Impersonation", "Reward/Greed", "Financial Pressure"], ["Payment"], "en"),
        ("Work from home typist needed. Earn $35/hour. Submit $50 security deposit for test materials via PayPal.", "Job Scam", "Request Payment", "LOW", ["Reward/Greed", "Financial Pressure"], ["Payment"], "en"),
        
        # Delivery variations
        ("UPS: We could not deliver your package #TR849201. Surcharge fee $2.50 required. Reschedule delivery here: {link}", "Delivery Scam", "Delivery Notification", "HIGH", ["Urgency", "Authority Impersonation"], ["Credit Card"], "en"),
        ("India Post: Parcel held at distribution hub due to unpaid customs duty of Rs 25. Clear immediately: {link}", "Delivery Scam", "Delivery Notification", "HIGH", ["Urgency", "Authority Impersonation"], ["Payment"], "en"),
        ("Aapka order delivery boy ke pass hai par contact number missing hai. Diye gaye link {link} par phone number aur OTP verify karein.", "Delivery Scam", "Delivery Notification", "HIGH", ["Urgency", "Trust Exploitation"], ["OTP", "Phone Number"], "hinglish"),
        
        # Fake Support variations
        ("CRITICAL SYSTEM ALERT: Trojan virus infected your Windows PC. Network breach in progress. Call support {phone} immediately.", "Fake Support", "Threat", "CRITICAL", ["Fear", "Urgency", "Authority Impersonation"], ["Remote Access"], "en"),
        ("Hello, this is telecom technical support. 5G tower upgrade requires SIM re-verification. Send 16 digit SIM number to prevent deactivation.", "Fake Support", "Customer Support", "HIGH", ["Authority Impersonation", "Fear"], ["SIM Number"], "en"),
        ("Aapke router par suspicious attack hua hai, main cyber department se baat kar raha hoon. Turant computer mein TeamViewer start karein.", "Fake Support", "Threat", "CRITICAL", ["Authority Impersonation", "Fear"], ["Remote Access"], "hinglish"),
        
        # Impersonation variations
        ("Hey, I lost my phone while traveling abroad and borrowing this number. Please wire $600 to hotel manager right away, I'll pay back tomorrow.", "Impersonation", "Request Payment", "CRITICAL", ["Emotional Pressure", "Urgency", "Trust Exploitation"], ["Wire Transfer"], "en"),
        ("CEO urgent request: I am in a confidential board meeting. Need you to purchase $500 Apple gift cards and email the redemption codes urgently.", "Impersonation", "Request Payment", "HIGH", ["Authority Impersonation", "Urgency", "Secrecy"], ["Gift Cards"], "en"),
        ("Main police station se bol raha hoon, aapke bete ko legal case mein arrest kiya gaya hai. Case settle karne ke liye abhi 50,000 transfer karo.", "Impersonation", "Threat", "CRITICAL", ["Fear", "Threat", "Emotional Pressure", "Urgency"], ["Payment"], "hinglish"),
        
        # Payment variations
        ("You have won Rs 5,000 scratch card on Google Pay! Tap link {link} and enter your UPI PIN to claim reward directly in bank.", "Payment Scam", "Prize/Reward", "HIGH", ["Reward/Greed", "Trust Exploitation"], ["UPI PIN"], "en"),
        ("Refund of $399.00 processed for Geek Squad service. To cancel automated charge, connect with our billing specialist at {phone}.", "Payment Scam", "Refund Request", "HIGH", ["Fear", "Financial Pressure"], ["Bank Details"], "en"),
        ("Aapko ₹2,500 ka cashback mila hai. Scan karein aur UPI PIN daalkar paise receive karein.", "Payment Scam", "Request Payment", "HIGH", ["Reward/Greed", "Trust Exploitation"], ["UPI PIN"], "hinglish"),
        
        # Romance variations
        ("My love, I bought diamond jewelry for our wedding but it is held at airport customs. Transfer customs fee $1,200 to officer account so I can meet you.", "Romance/Social Engineering", "Request Payment", "HIGH", ["Emotional Pressure", "Trust Exploitation", "Urgency"], ["Payment"], "en"),
        ("Darling, keep this between us. My bank accounts are frozen due to confidential mission. Send me $500 in Bitcoin for emergency medical supplies.", "Romance/Social Engineering", "Request Payment", "HIGH", ["Emotional Pressure", "Secrecy", "Trust Exploitation"], ["Crypto Wallet", "Payment"], "en"),
        
        # Prize/Reward variations
        ("Lucky Draw Winner: Selected phone number won Rs 10,00,000 in Mega Diwali contest! Pay government tax Rs 3,500 to release prize money.", "Prize/Reward Scam", "Prize/Reward", "MEDIUM", ["Reward/Greed", "Authority Impersonation"], ["Payment"], "en"),
        ("Aapka number KBC contest mein lucky draw winner ban gaya hai. Manager se baat karein aur 25 lakh ka cheque paayein.", "Prize/Reward Scam", "Prize/Reward", "MEDIUM", ["Reward/Greed"], ["Personal Information"], "hinglish"),
        
        # Account Verification variations
        ("Important: Complete your mandatory Aadhaar e-KYC update within 24 hours at {link} or your telecom SIM will be deactivated permanently.", "Account Verification Scam", "Account Verification", "HIGH", ["Urgency", "Fear", "Account Suspension Pressure"], ["Aadhaar", "KYC Documents"], "en"),
        ("NetBanking Security: Your account requires mandatory multi-factor re-registration. Follow {link} to submit credentials and secret questions.", "Account Verification Scam", "Account Verification", "HIGH", ["Authority Impersonation", "Urgency"], ["Login Credentials", "Security Questions"], "en"),
        
        # Credential Theft variations
        ("Corporate IT Alert: Password for your corporate single sign-on will expire in 1 hour. Keep existing password by confirming here: {link}", "Credential Theft", "Credential Harvesting", "HIGH", ["Urgency", "Time Pressure", "Authority Impersonation"], ["Password"], "en"),
        ("Webmail Administrator: Mailbox quota exceeded. Verify login credentials at {link} to prevent immediate deletion of stored mail.", "Credential Theft", "Credential Harvesting", "HIGH", ["Urgency", "Scarcity", "Fear"], ["Password", "Username"], "en"),
        
        # Legitimate variations
        ("Hi {name}, our project sync is scheduled for 3 PM on Zoom today. Meeting ID and agenda are on Google Calendar.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "en"),
        ("Dear customer, your electricity bill of Rs {amt} is due on 25th of this month. Pay safely via our official app or consumer portal.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "en"),
        ("Your Amazon order #{acc} has been shipped via BlueDart. Track package status on Amazon mobile app or website.", "Legitimate / Safe", "Delivery Notification", "LOW", [], [], "en"),
        ("Bhai assignment submit kar diya kya? Agar ho gaya ho toh reference ke liye send kar dena please.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "hinglish"),
        ("Your flight 6E-204 from Mumbai to Delhi is on schedule. Web check-in opens 48 hours prior to departure.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "en"),
        ("Thank you for your payment of Rs {amt} towards broadband subscription. Transaction ID: TXN948201.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "en"),
        ("Aaj sham ko football match hai college ground mein, sab 5 baje pahuch jana time se.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "hinglish"),
        ("Doctor's prescription and lab test report for CBC are ready for download from the official hospital patient portal.", "Legitimate / Safe", "Legitimate Inquiry", "LOW", [], [], "en")
    ]
    
    banks = ["SBI", "HDFC", "ICICI", "Axis Bank", "Kotak", "Punjab National Bank", "Bank of Baroda"]
    services = ["Google", "Microsoft", "Netflix", "PayPal", "Amazon", "Apple", "Instagram"]
    names = ["Priya", "Rahul", "Aman", "Sneha", "Rohit", "Ananya", "Vikram", "Neha"]
    links = ["http://secure-login-portal.co", "http://update-kyc-desk.net", "http://bank-auth-verify.xyz", "http://portal-account-service.top"]
    
    for template, cat, intent, urg, cues, sens, lang in variations:
        for i in range(5):  # Create multiple concrete instances
            bank = random.choice(banks)
            service = random.choice(services)
            name = random.choice(names)
            link = random.choice(links)
            amt = random.choice([500, 1500, 4800, 12000, 25000, 50000])
            ret = amt * random.choice([3, 5, 10])
            acc = f"XX{random.randint(1000, 9999)}"
            otp = str(random.randint(100000, 999999))
            phone = f"+91-98{random.randint(10000000, 99999999)}"
            time_val = random.choice([1, 2, 4, 12, 24])
            merchant = random.choice(["Flipkart", "Myntra", "CryptoPay", "International Gateway"])
            
            text = template.format(
                bank=bank, service=service, name=name, link=link,
                amt=amt, ret=ret, acc=acc, otp=otp, phone=phone,
                time=time_val, merchant=merchant
            )
            
            records.append({
                "text": text,
                "category": cat,
                "intent": intent,
                "urgency": urg,
                "manipulation_techniques": cues,
                "sensitive_requested": sens,
                "language": lang
            })
            
    return records

if __name__ == "__main__":
    records = generate_expanded_dataset()
    print(f"Total dataset records generated: {len(records)}")
    
    df = pd.DataFrame(records)
    print("Class distribution:")
    print(df['category'].value_counts())
    
    # Save processed dataset
    output_path = os.path.join("data", "processed", "scam_dataset.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        
    csv_path = os.path.join("data", "processed", "scam_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully saved to {output_path} and {csv_path}")
