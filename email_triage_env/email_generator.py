"""
Email dataset generator for the Email Triage Environment.

Generates realistic, deterministic email datasets for triage tasks.
Each email has a ground-truth category, priority, and action items.
"""

import random
from typing import Any, Dict, List, Optional


# =============================================================================
# Email Templates — organized by category
# =============================================================================

SPAM_EMAILS = [
    {
        "subject": "You've Won $1,000,000!!! Claim Now!!!",
        "from": "prize-winner@totally-legit-prizes.com",
        "body": (
            "Congratulations! You have been selected as the winner of our "
            "international lottery. To claim your $1,000,000 prize, please "
            "send your bank details and a processing fee of $500 to the "
            "address below. This offer expires in 24 hours! Act now!"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "URGENT: Your account has been compromised",
        "from": "security@paypa1-alerts.com",
        "body": (
            "We detected suspicious activity on your account. Your account "
            "will be suspended unless you verify your identity immediately. "
            "Click the link below to confirm your password and social security "
            "number. Failure to act within 12 hours will result in permanent "
            "account closure. http://paypa1-verify.suspicious-site.com/login"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Get Rich Quick - No Effort Required!",
        "from": "money-maker@instant-wealth.biz",
        "body": (
            "Are you tired of working hard for little pay? Our revolutionary "
            "system has helped thousands earn $10,000 per week from home! "
            "No experience needed. Just sign up with a small investment of "
            "$99 and start earning today! Limited spots available."
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Cheap Medications - 90% Off!",
        "from": "pharmacy-deals@discount-meds.xyz",
        "body": (
            "Save up to 90% on all prescription medications! No prescription "
            "needed. We ship worldwide with discreet packaging. Order now and "
            "get free shipping on orders over $50. All major brands available."
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Hot Singles in Your Area Want to Meet You",
        "from": "matches@dating-now-free.com",
        "body": (
            "You have 15 new matches waiting for you! Beautiful singles in "
            "your area are eager to connect. Create your profile today and "
            "start chatting for free. Premium membership unlocks exclusive "
            "features. Don't miss out on love!"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Bitcoin Investment Opportunity - 500% Returns!",
        "from": "crypto-guru@blockchain-profits.io",
        "body": (
            "Our AI-powered trading bot guarantees 500% returns on your "
            "Bitcoin investment within 30 days. Minimum investment: $250. "
            "Join 50,000+ happy investors. Risk-free with our money-back "
            "guarantee. Limited time offer!"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "You are the beneficiary of $15.5 million USD",
        "from": "barr.james@diplomat-office.org",
        "body": (
            "Dear Beneficiary, I am Barrister James from the United Nations. "
            "A deceased client left $15.5 million with your name as the next "
            "of kin. Please provide your full name, address, phone number, "
            "and a copy of your ID to begin the transfer process. Regards."
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "FREE iPhone 16 - Just Complete a Survey!",
        "from": "rewards@apple-giveaway-2024.com",
        "body": (
            "You've been selected to receive a brand new iPhone 16 Pro Max! "
            "Simply complete our 2-minute survey and pay a small shipping fee "
            "of $9.99. Hurry - only 3 phones left! This exclusive offer is "
            "only available for the next 30 minutes."
        ),
        "priority": "low",
        "action_items": [],
    },
]

WORK_EMAILS = [
    {
        "subject": "Q3 Budget Review Meeting - Thursday 2pm",
        "from": "sarah.chen@company.com",
        "body": (
            "Hi team,\n\nI'd like to schedule our Q3 budget review meeting "
            "for this Thursday at 2pm in Conference Room B. Please bring your "
            "department's spending reports and projections for Q4.\n\n"
            "Key agenda items:\n"
            "1. Review Q3 actual vs. planned spending\n"
            "2. Identify cost-saving opportunities\n"
            "3. Discuss Q4 budget allocations\n\n"
            "Please confirm your attendance by end of day tomorrow.\n\n"
            "Best,\nSarah"
        ),
        "priority": "medium",
        "action_items": [
            "Prepare department spending reports",
            "Prepare Q4 projections",
            "Confirm attendance by tomorrow",
            "Attend meeting Thursday 2pm",
        ],
    },
    {
        "subject": "Code Review Required: PR #1247 - Authentication Module",
        "from": "dev.ops@company.com",
        "body": (
            "Hi,\n\nA new pull request has been submitted that requires your "
            "review:\n\nPR #1247: Refactor authentication module to support "
            "OAuth 2.0\nAuthor: Mike Johnson\nBranch: feature/oauth2-support\n"
            "Files changed: 23\nLines: +847 / -312\n\n"
            "This PR introduces breaking changes to the auth API. Please "
            "review before Friday EOD as this blocks the v2.0 release.\n\n"
            "Review link: https://github.com/company/repo/pull/1247"
        ),
        "priority": "high",
        "action_items": [
            "Review PR #1247",
            "Check breaking changes to auth API",
            "Complete review before Friday EOD",
        ],
    },
    {
        "subject": "Updated Project Timeline - Client Deliverables",
        "from": "pm.lisa@company.com",
        "body": (
            "Team,\n\nBased on our discussion yesterday, here is the updated "
            "project timeline:\n\n"
            "- Phase 1 (Design): Complete by April 15\n"
            "- Phase 2 (Development): April 16 - May 30\n"
            "- Phase 3 (Testing): June 1 - June 15\n"
            "- Client Demo: June 20\n\n"
            "Please update your individual task estimates in Jira by Friday. "
            "Let me know if any of these dates are unrealistic for your team.\n\n"
            "Thanks,\nLisa"
        ),
        "priority": "medium",
        "action_items": [
            "Update task estimates in Jira by Friday",
            "Review timeline for feasibility",
            "Flag any unrealistic dates",
        ],
    },
    {
        "subject": "Onboarding: New Team Member Starting Monday",
        "from": "hr@company.com",
        "body": (
            "Hi,\n\nJust a reminder that Alex Rivera will be joining your "
            "team on Monday as a Senior Developer. Could you please:\n\n"
            "1. Prepare their workstation and access credentials\n"
            "2. Set up a welcome meeting for 10am Monday\n"
            "3. Assign a buddy for the first two weeks\n"
            "4. Share the team wiki and coding guidelines\n\n"
            "Let me know if you need anything from HR to support the "
            "onboarding process.\n\nThanks,\nHR Team"
        ),
        "priority": "high",
        "action_items": [
            "Prepare workstation and access credentials",
            "Set up welcome meeting Monday 10am",
            "Assign onboarding buddy",
            "Share team wiki and coding guidelines",
        ],
    },
    {
        "subject": "Weekly Status Report - Week 14",
        "from": "reports@company.com",
        "body": (
            "Please submit your weekly status report for Week 14 by Friday "
            "5pm. Include:\n\n"
            "- Completed tasks this week\n"
            "- Planned tasks for next week\n"
            "- Blockers or risks\n"
            "- Key metrics/KPIs\n\n"
            "Submit via the project management portal."
        ),
        "priority": "medium",
        "action_items": [
            "Submit weekly status report by Friday 5pm",
            "Document completed tasks",
            "Plan tasks for next week",
            "Identify blockers and risks",
        ],
    },
    {
        "subject": "Server Downtime Notice - Saturday Maintenance",
        "from": "it-ops@company.com",
        "body": (
            "Heads up team,\n\nScheduled server maintenance this Saturday "
            "from 2am to 6am EST. The following services will be affected:\n\n"
            "- CI/CD Pipeline\n- Staging environment\n- Internal wiki\n\n"
            "Production systems will NOT be affected. Please plan your work "
            "accordingly and avoid deploying to staging during this window.\n\n"
            "IT Operations"
        ),
        "priority": "low",
        "action_items": [
            "Avoid staging deployments Saturday 2am-6am",
            "Plan work around downtime",
        ],
    },
    {
        "subject": "Performance Review - Schedule Your Session",
        "from": "manager@company.com",
        "body": (
            "Hi,\n\nIt's time for our annual performance review cycle. "
            "Please schedule a 1-hour session with me before April 30. "
            "Before our meeting, please:\n\n"
            "1. Complete your self-assessment form\n"
            "2. Gather peer feedback from at least 3 colleagues\n"
            "3. Prepare your goals for next year\n\n"
            "Self-assessment form: https://internal.company.com/perf-review\n\n"
            "Looking forward to our discussion.\nBest regards"
        ),
        "priority": "medium",
        "action_items": [
            "Schedule performance review session before April 30",
            "Complete self-assessment form",
            "Gather peer feedback from 3 colleagues",
            "Prepare goals for next year",
        ],
    },
]

PERSONAL_EMAILS = [
    {
        "subject": "Happy Birthday! 🎂",
        "from": "mom@gmail.com",
        "body": (
            "Happy Birthday sweetheart! 🎂🎉\n\n"
            "Wishing you a wonderful day filled with joy and laughter. "
            "Dad and I are so proud of you! We can't wait to celebrate "
            "with you this weekend. I'm making your favorite cake!\n\n"
            "Love always,\nMom & Dad ❤️"
        ),
        "priority": "low",
        "action_items": [
            "Reply with thanks",
            "Confirm weekend plans",
        ],
    },
    {
        "subject": "Reunion Dinner - RSVP by Friday",
        "from": "college-group@gmail.com",
        "body": (
            "Hey everyone!\n\nWe're organizing a college reunion dinner on "
            "April 25th at 7pm at The Grand Restaurant downtown. It's been "
            "5 years since graduation!\n\n"
            "Please RSVP by this Friday so we can book the right table size. "
            "Partners are welcome! Cost will be split equally.\n\n"
            "Can't wait to see you all!\nRaj"
        ),
        "priority": "low",
        "action_items": [
            "RSVP by Friday",
            "Note dinner date April 25th 7pm",
        ],
    },
    {
        "subject": "Photos from last weekend's trip",
        "from": "friend.anita@gmail.com",
        "body": (
            "Hey! Here are the photos from our hiking trip last weekend. "
            "I uploaded them to Google Photos - sharing the album link below.\n\n"
            "https://photos.google.com/share/album123\n\n"
            "Some amazing shots of the sunset! Let me know your favorites "
            "and I'll print them for you. Also, when are we planning the next trip?\n\n"
            "Cheers,\nAnita"
        ),
        "priority": "low",
        "action_items": [
            "Check shared photo album",
            "Reply with favorite photos",
        ],
    },
    {
        "subject": "Apartment Lease Renewal Notice",
        "from": "landlord@property-mgmt.com",
        "body": (
            "Dear Tenant,\n\nYour current lease expires on May 31, 2026. "
            "We would like to offer you a renewal at the following terms:\n\n"
            "- Duration: 12 months (June 1, 2026 - May 31, 2027)\n"
            "- Monthly rent: $1,850 (increase of $50 from current)\n"
            "- Same deposit terms apply\n\n"
            "Please confirm your intention to renew or vacate by April 30. "
            "If renewing, sign the attached lease agreement and return it "
            "to our office.\n\nBest regards,\nProperty Management"
        ),
        "priority": "medium",
        "action_items": [
            "Decide on lease renewal by April 30",
            "Review new rental terms",
            "Sign and return lease if renewing",
        ],
    },
    {
        "subject": "Dentist Appointment Reminder",
        "from": "no-reply@smileclinic.com",
        "body": (
            "This is a reminder of your upcoming dental appointment:\n\n"
            "Date: April 12, 2026\nTime: 10:30 AM\n"
            "Doctor: Dr. Patel\nClinic: Smile Dental Clinic\n"
            "Address: 123 Health Street, Suite 4B\n\n"
            "Please arrive 15 minutes early for check-in. "
            "If you need to reschedule, call us at (555) 123-4567."
        ),
        "priority": "low",
        "action_items": [
            "Note appointment April 12 at 10:30 AM",
            "Arrive 15 minutes early",
        ],
    },
]

URGENT_EMAILS = [
    {
        "subject": "🚨 PRODUCTION DOWN - Immediate Action Required",
        "from": "monitoring@company.com",
        "body": (
            "ALERT: Production service is DOWN.\n\n"
            "Service: payment-api\n"
            "Status: 503 Service Unavailable\n"
            "Started: 2026-04-07 14:32 UTC\n"
            "Impact: All payment transactions are failing\n"
            "Affected users: ~50,000\n\n"
            "Last deploy: 2 hours ago by deploy-bot\n"
            "Error logs show: OutOfMemoryError in payment-worker pods\n\n"
            "Please join the incident channel #inc-payment-down immediately. "
            "On-call engineer has been paged."
        ),
        "priority": "critical",
        "action_items": [
            "Join incident channel #inc-payment-down immediately",
            "Investigate OutOfMemoryError in payment-worker pods",
            "Consider rolling back last deploy",
            "Update incident status page",
        ],
    },
    {
        "subject": "SECURITY BREACH: Unauthorized Access Detected",
        "from": "security-team@company.com",
        "body": (
            "CRITICAL SECURITY ALERT\n\n"
            "Unauthorized access has been detected on our database servers. "
            "Details:\n\n"
            "- Timestamp: 2026-04-07 13:45 UTC\n"
            "- Source IP: 192.168.45.89 (unknown/external)\n"
            "- Tables accessed: users, payment_methods\n"
            "- Records potentially exposed: ~10,000\n\n"
            "IMMEDIATE ACTIONS REQUIRED:\n"
            "1. Rotate all database credentials NOW\n"
            "2. Block the source IP in firewall\n"
            "3. Begin forensic analysis\n"
            "4. Prepare incident report for CISO\n\n"
            "Do NOT discuss this on public channels."
        ),
        "priority": "critical",
        "action_items": [
            "Rotate all database credentials immediately",
            "Block source IP 192.168.45.89 in firewall",
            "Begin forensic analysis",
            "Prepare incident report for CISO",
        ],
    },
    {
        "subject": "Client Escalation - Contract at Risk",
        "from": "vp.sales@company.com",
        "body": (
            "URGENT - Need response within 1 hour\n\n"
            "Our largest client (TechCorp, $2M annual contract) has "
            "escalated a critical issue. Their integration has been broken "
            "for 3 days and they are threatening to terminate the contract.\n\n"
            "They need:\n"
            "1. A root cause analysis by end of today\n"
            "2. A fix deployed within 24 hours\n"
            "3. A call with our CTO tomorrow at 9am\n\n"
            "This is our top priority. Please drop everything else and focus "
            "on this. I need an update in 1 hour.\n\n"
            "- VP Sales"
        ),
        "priority": "critical",
        "action_items": [
            "Investigate TechCorp integration issue immediately",
            "Prepare root cause analysis by end of today",
            "Deploy fix within 24 hours",
            "Schedule CTO call for tomorrow 9am",
            "Send update within 1 hour",
        ],
    },
    {
        "subject": "Emergency: Office Evacuation Drill Tomorrow",
        "from": "facilities@company.com",
        "body": (
            "IMPORTANT NOTICE\n\n"
            "A mandatory fire evacuation drill will be conducted tomorrow "
            "(April 8) at 11:00 AM. All employees must:\n\n"
            "1. Save all work and close laptops at 10:55 AM\n"
            "2. Proceed to the nearest emergency exit calmly\n"
            "3. Gather at the designated assembly point (Parking Lot B)\n"
            "4. Wait for the all-clear signal before returning\n\n"
            "Floor wardens, please report to the Safety Office at 10:30 AM "
            "for briefing.\n\nThis is not optional. Non-compliance will be "
            "reported to department heads."
        ),
        "priority": "high",
        "action_items": [
            "Save work by 10:55 AM tomorrow",
            "Participate in evacuation drill at 11 AM",
            "Proceed to Parking Lot B assembly point",
        ],
    },
    {
        "subject": "Deadline Extended: Tax Documents Due April 15",
        "from": "accounting@company.com",
        "body": (
            "REMINDER: Tax related documents must be submitted by April 15.\n\n"
            "We still haven't received the following from you:\n"
            "- Updated W-4 form\n"
            "- Home office expense receipts\n"
            "- Investment income documentation\n\n"
            "Failure to submit by April 15 will result in delayed tax "
            "processing and potential penalties. Please upload documents "
            "to the HR portal immediately.\n\n"
            "Finance Department"
        ),
        "priority": "high",
        "action_items": [
            "Submit updated W-4 form",
            "Upload home office expense receipts",
            "Submit investment income documentation",
            "Complete by April 15 deadline",
        ],
    },
]

NEWSLETTER_EMAILS = [
    {
        "subject": "This Week in AI - Top 10 Papers You Shouldn't Miss",
        "from": "newsletter@ai-weekly.com",
        "body": (
            "Welcome to This Week in AI! 🤖\n\n"
            "Top stories:\n"
            "1. GPT-5 rumors: What we know so far\n"
            "2. New breakthrough in protein folding\n"
            "3. Open-source LLM beats proprietary models\n"
            "4. EU AI Act: What developers need to know\n"
            "5. Tutorial: Building RAG applications\n\n"
            "Read the full newsletter: https://ai-weekly.com/issue-142\n\n"
            "Happy reading!\n"
            "The AI Weekly Team\n\n"
            "Unsubscribe: https://ai-weekly.com/unsubscribe"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Your Monthly GitHub Activity Report",
        "from": "noreply@github.com",
        "body": (
            "Here's your monthly GitHub report for March 2026:\n\n"
            "📊 Activity Summary:\n"
            "- 47 contributions\n"
            "- 12 pull requests merged\n"
            "- 5 issues closed\n"
            "- 3 repositories starred\n\n"
            "🔥 Your longest streak: 14 days\n"
            "⭐ Most active repo: openenv-project\n\n"
            "Keep up the great work! View your full profile at "
            "https://github.com/yourprofile"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Udemy: Flash Sale - Courses Starting at $9.99",
        "from": "promotions@udemy.com",
        "body": (
            "🔥 Flash Sale - 48 Hours Only! 🔥\n\n"
            "Courses starting at just $9.99!\n\n"
            "Top picks for you:\n"
            "- Advanced Python Programming: $9.99 (was $89.99)\n"
            "- Machine Learning A-Z: $12.99 (was $94.99)\n"
            "- Docker & Kubernetes Masterclass: $9.99 (was $79.99)\n\n"
            "Sale ends in 48 hours!\n"
            "Shop now: https://udemy.com/sale\n\n"
            "Unsubscribe from promotional emails"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "Dev.to Digest: Most Popular Posts This Week",
        "from": "digest@dev.to",
        "body": (
            "Here are the most popular Dev.to posts this week:\n\n"
            "1. 'Why I switched from React to Svelte' - 2.3k reactions\n"
            "2. 'Building a CLI tool with Rust' - 1.8k reactions\n"
            "3. 'Understanding async/await in JavaScript' - 1.5k reactions\n"
            "4. 'My journey from bootcamp to FAANG' - 1.2k reactions\n\n"
            "Read more at https://dev.to\n\n"
            "Manage notification preferences"
        ),
        "priority": "low",
        "action_items": [],
    },
    {
        "subject": "AWS re:Invent 2026 - Early Bird Registration Open",
        "from": "events@aws.amazon.com",
        "body": (
            "AWS re:Invent 2026 is coming!\n\n"
            "📅 Date: November 30 - December 4, 2026\n"
            "📍 Location: Las Vegas, NV\n\n"
            "Early bird pricing: $1,499 (regular: $2,099)\n"
            "Register by June 30 to save!\n\n"
            "This year's highlights:\n"
            "- 2,000+ sessions\n"
            "- Hands-on labs\n"
            "- Certification bootcamps\n"
            "- Networking events\n\n"
            "Register now: https://reinvent.awsevents.com"
        ),
        "priority": "low",
        "action_items": [],
    },
]

# Category to email list mapping
CATEGORY_EMAILS = {
    "spam": SPAM_EMAILS,
    "work": WORK_EMAILS,
    "personal": PERSONAL_EMAILS,
    "urgent": URGENT_EMAILS,
    "newsletter": NEWSLETTER_EMAILS,
}

# Thread templates for hard-mode tasks
EMAIL_THREADS = [
    {
        "subject": "RE: Project Alpha - Architecture Decision",
        "from": "tech.lead@company.com",
        "thread": [
            {
                "from": "pm.lisa@company.com",
                "date": "2026-04-05 09:00",
                "body": (
                    "Team, we need to finalize the architecture for Project Alpha. "
                    "Options are microservices or monolith. Please share your thoughts."
                ),
            },
            {
                "from": "senior.dev@company.com",
                "date": "2026-04-05 10:30",
                "body": (
                    "I recommend microservices for scalability, but it adds complexity. "
                    "We'd need to set up service mesh and API gateway. Timeline impact: +2 weeks."
                ),
            },
            {
                "from": "tech.lead@company.com",
                "date": "2026-04-05 14:00",
                "body": (
                    "After reviewing both options, I agree with microservices. However, "
                    "we need to:\n"
                    "1. Define service boundaries by Friday\n"
                    "2. Set up CI/CD for multi-service deployment\n"
                    "3. Choose between gRPC and REST for inter-service communication\n"
                    "4. Get client approval for the 2-week timeline extension\n\n"
                    "Can everyone provide their input by tomorrow EOD?"
                ),
            },
        ],
        "category": "work",
        "priority": "high",
        "action_items": [
            "Define service boundaries by Friday",
            "Provide input on architecture by tomorrow EOD",
            "Evaluate gRPC vs REST for inter-service communication",
            "Help get client approval for timeline extension",
        ],
    },
    {
        "subject": "RE: Bug Report - Payment Processing Failure",
        "from": "qa.team@company.com",
        "thread": [
            {
                "from": "customer.support@company.com",
                "date": "2026-04-06 08:00",
                "body": (
                    "We're getting multiple reports of payment failures from customers. "
                    "Error: 'Transaction declined - gateway timeout'. Affects credit card "
                    "payments only. PayPal and bank transfers work fine."
                ),
            },
            {
                "from": "payment.team@company.com",
                "date": "2026-04-06 09:15",
                "body": (
                    "Investigated - the issue is with our Stripe webhook handler. "
                    "The timeout is set to 5 seconds but some transactions take longer. "
                    "Quick fix: increase timeout to 30 seconds. Long-term: implement "
                    "async payment processing with queue."
                ),
            },
            {
                "from": "qa.team@company.com",
                "date": "2026-04-06 11:00",
                "body": (
                    "I've verified the fix in staging. Increasing timeout to 30s resolves "
                    "the issue. However, I found another edge case: concurrent payments "
                    "from the same user can cause race conditions. We should:\n"
                    "1. Deploy the timeout fix to production ASAP\n"
                    "2. Add idempotency keys to prevent duplicate charges\n"
                    "3. Add monitoring alerts for payment gateway latency\n"
                    "4. Update the incident runbook\n\n"
                    "Who can deploy the hotfix today?"
                ),
            },
        ],
        "category": "urgent",
        "priority": "critical",
        "action_items": [
            "Deploy timeout fix to production ASAP",
            "Add idempotency keys to payment processing",
            "Set up monitoring alerts for payment gateway latency",
            "Update incident runbook",
            "Volunteer to deploy hotfix today",
        ],
    },
    {
        "subject": "RE: Team Outing Planning",
        "from": "social.committee@company.com",
        "thread": [
            {
                "from": "social.committee@company.com",
                "date": "2026-04-04 12:00",
                "body": (
                    "Hey team! Time to plan our quarterly outing. Options:\n"
                    "A) Bowling + dinner\nB) Escape room + drinks\n"
                    "C) Outdoor BBQ at the park\n\nVote by replying with A, B, or C!"
                ),
            },
            {
                "from": "colleague1@company.com",
                "date": "2026-04-04 12:30",
                "body": "B sounds awesome! I love escape rooms.",
            },
            {
                "from": "colleague2@company.com",
                "date": "2026-04-04 13:00",
                "body": (
                    "C gets my vote! Weather should be nice. Also, I can bring my "
                    "portable speaker and lawn games. When are we thinking - next "
                    "Friday or the Friday after? Need to check if the park requires "
                    "a reservation for large groups."
                ),
            },
        ],
        "category": "personal",
        "priority": "low",
        "action_items": [
            "Vote on team outing option (A, B, or C)",
            "Check availability for proposed dates",
        ],
    },
]


def generate_email_dataset(
    seed: int = 42,
    num_per_category: int = 5,
    include_threads: bool = False,
) -> List[Dict[str, Any]]:
    """
    Generate a deterministic email dataset.

    Args:
        seed: Random seed for reproducibility
        num_per_category: Number of emails per category
        include_threads: Whether to include threaded emails

    Returns:
        List of email dicts with ground truth labels
    """
    rng = random.Random(seed)
    dataset = []
    email_id = 0

    for category, emails in CATEGORY_EMAILS.items():
        # Select emails (with repetition if needed)
        selected = []
        for i in range(num_per_category):
            selected.append(emails[i % len(emails)])

        rng.shuffle(selected)

        for email in selected:
            email_id += 1
            dataset.append(
                {
                    "id": f"email-{email_id:04d}",
                    "subject": email["subject"],
                    "from": email["from"],
                    "to": "user@company.com",
                    "date": f"2026-04-{rng.randint(1, 28):02d} {rng.randint(6, 22):02d}:{rng.randint(0, 59):02d}",
                    "body": email["body"],
                    "category": category,
                    "priority": email["priority"],
                    "action_items": email.get("action_items", []),
                    "thread": None,
                }
            )

    if include_threads:
        for thread_data in EMAIL_THREADS:
            email_id += 1
            dataset.append(
                {
                    "id": f"email-{email_id:04d}",
                    "subject": thread_data["subject"],
                    "from": thread_data["from"],
                    "to": "user@company.com",
                    "date": "2026-04-07 15:00",
                    "body": thread_data["thread"][-1]["body"],
                    "category": thread_data["category"],
                    "priority": thread_data["priority"],
                    "action_items": thread_data.get("action_items", []),
                    "thread": thread_data["thread"],
                }
            )

    rng.shuffle(dataset)
    return dataset


def get_email_by_index(
    index: int,
    seed: int = 42,
    task_difficulty: str = "easy",
) -> Optional[Dict[str, Any]]:
    """
    Get a specific email from the dataset by index.

    Args:
        index: Email index (wraps around)
        seed: Random seed
        task_difficulty: Difficulty level determines dataset features

    Returns:
        Email dict or None
    """
    include_threads = task_difficulty == "hard"
    dataset = generate_email_dataset(
        seed=seed,
        num_per_category=5,
        include_threads=include_threads,
    )
    if not dataset:
        return None
    return dataset[index % len(dataset)]
