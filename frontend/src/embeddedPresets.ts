// Embedded preset inboxes for standalone/public demo execution
import type { NotificationItem, PresetInfo, BenchmarkMetrics } from './types';

export const EMBEDDED_PRESETS_LIST: PresetInfo[] = [
  {
    id: 'chaotic_monday',
    name: 'Chaotic Monday Morning',
    item_count: 28,
    description: 'Realistic engineering inbox with 28 overlapping Slack DMs, GitHub mentions, Linear blockers, and PagerDuty alerts.',
    sources: ['Slack', 'GitHub', 'Jira', 'PagerDuty', 'Email', 'Linear'],
  },
  {
    id: 'devops_alert_storm',
    name: 'DevOps Alert Storm',
    item_count: 22,
    description: 'Cascading infrastructure failure: OOMKill spikes, Redis latency warnings, automated healthchecks, and SSM rotation notices.',
    sources: ['Datadog', 'Kubernetes', 'Sentry', 'Slack', 'AWS SSM'],
  },
  {
    id: 'maintainer_backlog',
    name: 'Maintainer Backlog',
    item_count: 35,
    description: 'High-volume open-source repository triage with duplicated beginner questions, bot alerts, and a critical YAML security advisory.',
    sources: ['GitHub Issues', 'GitHub PRs', 'Security Advisories', 'Discord'],
  },
];

export const EMBEDDED_DATASETS: Record<string, NotificationItem[]> = {
  chaotic_monday: [
  {
    "id": "notif-001",
    "source": "Slack",
    "sender": "sarah.chen (Engineering Lead)",
    "timestamp": "2026-10-23T08:15:00Z",
    "title": "URGENT: Production Auth Gateway Latency Spike",
    "body": "Hey team, auth gateway p99 latency spiked past 1400ms in us-east-1. We need a rollback or DB connection pool increase before the 10:00 AM customer webinar. Who can jump on this right now?"
  },
  {
    "id": "notif-002",
    "source": "Slack",
    "sender": "sarah.chen (Engineering Lead)",
    "timestamp": "2026-10-23T08:22:00Z",
    "title": "URGENT reminder: Auth Gateway Latency",
    "body": "Following up on my message earlier: auth gateway latency is still climbing. @channel please check DB pool connections before 10:00 AM."
  },
  {
    "id": "notif-003",
    "source": "PagerDuty",
    "sender": "AlertBot",
    "timestamp": "2026-10-23T08:18:00Z",
    "title": "[Triggered] Auth-Service-US-East-P99-High",
    "body": "Incident #4492: Auth Service latency exceeds SLO threshold (1450ms > 250ms). Impact: 8% of login requests delayed."
  },
  {
    "id": "notif-004",
    "source": "PagerDuty",
    "sender": "AlertBot",
    "timestamp": "2026-10-23T08:24:00Z",
    "title": "[Triggered] Auth-Service-US-East-P99-High (Escalated)",
    "body": "Incident #4492 escalated to Tier-2 SRE on-call. Condition active for 10 minutes."
  },
  {
    "id": "notif-005",
    "source": "GitHub",
    "sender": "security-bot",
    "timestamp": "2026-10-23T08:30:00Z",
    "title": "[Security Advisory] Critical vuln in pyjwt < 2.9.0",
    "body": "High severity CVE-2026-3829 detected in auth service requirements.txt. Fix available in version 2.9.1. Requires dependency bump and verification."
  },
  {
    "id": "notif-006",
    "source": "GitHub",
    "sender": "dependabot[bot]",
    "timestamp": "2026-10-23T08:31:00Z",
    "title": "Bump pyjwt from 2.8.0 to 2.9.1 in /backend",
    "body": "Bumps pyjwt from 2.8.0 to 2.9.1. Resolves security vulnerability CVE-2026-3829. CI checks pending."
  },
  {
    "id": "notif-007",
    "source": "Slack",
    "sender": "alex.m (Product Manager)",
    "timestamp": "2026-10-23T08:35:00Z",
    "title": "Q4 Roadmap Slides Review",
    "body": "Hi all! When you get a chance today or tomorrow, please take a quick look at the draft Q4 roadmap slide deck and leave comments."
  },
  {
    "id": "notif-008",
    "source": "Email",
    "sender": "Alex Miller <alex.m@company.com>",
    "timestamp": "2026-10-23T08:36:00Z",
    "title": "Draft Q4 Roadmap Slides for review",
    "body": "Team, attaching the Google Slides link for Q4 roadmap. No rush, review by end of week if possible."
  },
  {
    "id": "notif-009",
    "source": "Google Calendar",
    "sender": "calendar-notification@google.com",
    "timestamp": "2026-10-23T08:45:00Z",
    "title": "Reminder: All Hands in 15 minutes",
    "body": "Weekly All-Hands meeting starting at 9:00 AM IST. Room: Virtual Zoom link attached."
  },
  {
    "id": "notif-010",
    "source": "Google Calendar",
    "sender": "calendar-notification@google.com",
    "timestamp": "2026-10-23T08:50:00Z",
    "title": "Reminder: All Hands in 10 minutes",
    "body": "Weekly All-Hands meeting starting at 9:00 AM IST. Room: Virtual Zoom link attached."
  },
  {
    "id": "notif-011",
    "source": "Slack",
    "sender": "hr-announcements",
    "timestamp": "2026-10-23T08:55:00Z",
    "title": "All Hands starting now!",
    "body": "All Hands is live in Zoom room 4. Please join with microphones muted."
  },
  {
    "id": "notif-012",
    "source": "Linear",
    "sender": "jordan.k (Staff Architect)",
    "timestamp": "2026-10-23T09:05:00Z",
    "title": "ENG-1082: Sign off on API Schema Migration before Deployment",
    "body": "Ganesh, we cannot deploy the v2 user profiles schema without your sign-off on the backwards-compatibility test. Hard cutoff is 2:00 PM today."
  },
  {
    "id": "notif-013",
    "source": "Email",
    "sender": "Jordan Kelly <jordan.k@company.com>",
    "timestamp": "2026-10-23T09:07:00Z",
    "title": "FWD: ENG-1082 Schema Migration Approval Needed",
    "body": "Sent this on Linear as well: need your explicit sign-off on the user profile schema migration before 2:00 PM so DevOps can schedule the migration window."
  },
  {
    "id": "notif-014",
    "source": "Jira",
    "sender": "jira-notifications@company.com",
    "timestamp": "2026-10-23T09:12:00Z",
    "title": "PROD-502 updated: Documentation for Redis Cache Key Expiry",
    "body": "Status changed from To Do to In Progress. Assignee: David. Priority: Low."
  },
  {
    "id": "notif-015",
    "source": "Jira",
    "sender": "jira-notifications@company.com",
    "timestamp": "2026-10-23T09:15:00Z",
    "title": "PROD-502 comment added by David",
    "body": "Updated the Confluence page with TTL recommendations. No action required."
  },
  {
    "id": "notif-016",
    "source": "Slack",
    "sender": "office-facilities",
    "timestamp": "2026-10-23T09:20:00Z",
    "title": "Cafeteria Lunch Menu for Today",
    "body": "Today's special: Mediterranean bowls and vegetable curry. Available from 12:30 PM."
  },
  {
    "id": "notif-017",
    "source": "Email",
    "sender": "Weekly Tech Newsletter <digest@techweekly.dev>",
    "timestamp": "2026-10-23T09:22:00Z",
    "title": "Top 10 Open-Source AI Trends in October 2026",
    "body": "Read about Gemma 2, on-device SLMs, edge agents, and Hacktoberfest highlights."
  },
  {
    "id": "notif-018",
    "source": "Slack",
    "sender": "david.r (Backend Eng)",
    "timestamp": "2026-10-23T09:25:00Z",
    "title": "Quick question on PR #792 tests",
    "body": "Hey Ganesh, did you see the test suite updates on the booth deletion endpoint? Looking really clean, nice job on the idempotency handling."
  },
  {
    "id": "notif-019",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T09:28:00Z",
    "title": "Workflow run succeeded: CI Tests for PR #792",
    "body": "Run #149 finished: 11 tests passed in 6.85s. All checks green."
  },
  {
    "id": "notif-020",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T09:30:00Z",
    "title": "Workflow run succeeded: Lint and Formatting for PR #792",
    "body": "Ruff format check passed. 0 violations found."
  },
  {
    "id": "notif-021",
    "source": "Slack",
    "sender": "finance-ops",
    "timestamp": "2026-10-23T09:35:00Z",
    "title": "Monthly Expense Reports Reminder",
    "body": "Reminder: All travel and software subscription expense reimbursements for October are due by October 31."
  },
  {
    "id": "notif-022",
    "source": "Email",
    "sender": "Finance Department <expenses@company.com>",
    "timestamp": "2026-10-23T09:36:00Z",
    "title": "Expense submissions deadline: October 31",
    "body": "Please submit any pending receipts into Expensify before midnight on October 31 to ensure timely reimbursement."
  },
  {
    "id": "notif-023",
    "source": "Slack",
    "sender": "cloud-billing-alerts",
    "timestamp": "2026-10-23T09:40:00Z",
    "title": "AWS Daily Spend Notification",
    "body": "Daily spend for October 22 was $142.10 (within expected baseline of $150.00)."
  },
  {
    "id": "notif-024",
    "source": "Slack",
    "sender": "random-chatter",
    "timestamp": "2026-10-23T09:42:00Z",
    "title": "Anyone up for coffee at 11?",
    "body": "Heading down to the 2nd floor espresso machine around 11 if anyone wants to grab a cup!"
  },
  {
    "id": "notif-025",
    "source": "GitHub",
    "sender": "stale-bot",
    "timestamp": "2026-10-23T09:45:00Z",
    "title": "Issue #319 marked as stale",
    "body": "This issue has had no activity in 45 days. It will be closed in 7 days if no update is provided."
  },
  {
    "id": "notif-026",
    "source": "Slack",
    "sender": "sarah.chen (Engineering Lead)",
    "timestamp": "2026-10-23T09:50:00Z",
    "title": "Auth incident update: Mitigated",
    "body": "Quick update: SRE scaled DB pool min connections from 10 to 40. P99 latency dropped back down to 180ms. Root cause postmortem meeting tomorrow."
  },
  {
    "id": "notif-027",
    "source": "PagerDuty",
    "sender": "AlertBot",
    "timestamp": "2026-10-23T09:51:00Z",
    "title": "[Resolved] Auth-Service-US-East-P99-High",
    "body": "Incident #4492 has been resolved by Sarah Chen. Alert duration: 33 minutes."
  },
  {
    "id": "notif-028",
    "source": "Slack",
    "sender": "jordan.k (Staff Architect)",
    "timestamp": "2026-10-23T09:55:00Z",
    "title": "Ping on ENG-1082 schema sign-off",
    "body": "Hey Ganesh, checking in on the schema sign-off. Please let me know once you've reviewed the test script!"
  }
],
  devops_alert_storm: [
  {
    "id": "alert-001",
    "source": "Datadog",
    "sender": "Monitors",
    "timestamp": "2026-10-23T04:10:00Z",
    "title": "[Alert] MemoryUsage > 92% on worker-pod-3b",
    "body": "Pod worker-pod-3b memory reached 94.2%. OOMKilled risk imminent. Restart backoff counter: 2."
  },
  {
    "id": "alert-002",
    "source": "Datadog",
    "sender": "Monitors",
    "timestamp": "2026-10-23T04:12:00Z",
    "title": "[Alert] MemoryUsage > 95% on worker-pod-3b",
    "body": "Pod worker-pod-3b memory reached 96.1%. Critical threshold exceeded."
  },
  {
    "id": "alert-003",
    "source": "Kubernetes",
    "sender": "kube-event-router",
    "timestamp": "2026-10-23T04:14:00Z",
    "title": "Pod worker-pod-3b terminated (OOMKilled)",
    "body": "Container worker in pod worker-pod-3b was terminated with exit code 137 (OOMKilled). Node: k8s-node-us-east-1a."
  },
  {
    "id": "alert-004",
    "source": "Kubernetes",
    "sender": "kube-event-router",
    "timestamp": "2026-10-23T04:15:00Z",
    "title": "Pod worker-pod-3b restarted",
    "body": "Container worker recreated. Current state: Running."
  },
  {
    "id": "alert-005",
    "source": "Sentry",
    "sender": "error-tracker",
    "timestamp": "2026-10-23T04:18:00Z",
    "title": "Uncaught ConnectionResetError in async worker queue",
    "body": "ConnectionResetError: Cannot write to redis://redis-master:6379 (socket closed). 42 occurrences in last 5 minutes."
  },
  {
    "id": "alert-006",
    "source": "Sentry",
    "sender": "error-tracker",
    "timestamp": "2026-10-23T04:20:00Z",
    "title": "Uncaught ConnectionResetError in async worker queue (108 events)",
    "body": "Issue #8102 spiking rapidly across all ingest workers. First seen at 04:15:00Z."
  },
  {
    "id": "alert-007",
    "source": "Slack",
    "sender": "ops-oncall",
    "timestamp": "2026-10-23T04:22:00Z",
    "title": "Redis master failover in progress",
    "body": "Sentinel detected master unresponsive. Promoting redis-replica-1 to master. Client connection blips expected for ~30s."
  },
  {
    "id": "alert-008",
    "source": "Slack",
    "sender": "ops-oncall",
    "timestamp": "2026-10-23T04:25:00Z",
    "title": "Redis failover completed successfully",
    "body": "Redis replica-1 is now primary. Sentry error rates returning to 0. Auto-healing complete."
  },
  {
    "id": "alert-009",
    "source": "AWS GuardDuty",
    "sender": "security-alerts@aws.amazon.com",
    "timestamp": "2026-10-23T04:30:00Z",
    "title": "Unusual API call from unfamiliar IP address",
    "body": "Principal: arn:aws:iam::123456789012:role/CI-Runner called DescribeInstances from IP 198.51.100.44 (GitHub Actions runner). Low severity informational."
  },
  {
    "id": "alert-010",
    "source": "GitHub",
    "sender": "dependabot[bot]",
    "timestamp": "2026-10-23T04:35:00Z",
    "title": "Bump certifi from 2024.7.4 to 2024.8.30",
    "body": "Bumps certifi to latest release. Automated security scan clean."
  },
  {
    "id": "alert-011",
    "source": "UptimeRobot",
    "sender": "alert@uptimerobot.com",
    "timestamp": "2026-10-23T04:40:00Z",
    "title": "Monitor UP: API Healthcheck (200 OK)",
    "body": "URL: https://api.prod.example.com/health. Response time: 42ms."
  },
  {
    "id": "alert-012",
    "source": "UptimeRobot",
    "sender": "alert@uptimerobot.com",
    "timestamp": "2026-10-23T05:40:00Z",
    "title": "Monitor UP: API Healthcheck (200 OK)",
    "body": "URL: https://api.prod.example.com/health. Response time: 39ms."
  },
  {
    "id": "alert-013",
    "source": "UptimeRobot",
    "sender": "alert@uptimerobot.com",
    "timestamp": "2026-10-23T06:40:00Z",
    "title": "Monitor UP: API Healthcheck (200 OK)",
    "body": "URL: https://api.prod.example.com/health. Response time: 44ms."
  },
  {
    "id": "alert-014",
    "source": "Slack",
    "sender": "security-officer",
    "timestamp": "2026-10-23T06:50:00Z",
    "title": "ACTION REQUIRED: Rotate Staging DB Admin Password by 5 PM",
    "body": "Routine 90-day secret rotation policy: the staging Postgres root password expires today at 5:00 PM. Update SSM Parameter Store /staging/db/password."
  },
  {
    "id": "alert-015",
    "source": "Jira",
    "sender": "SEC-419",
    "timestamp": "2026-10-23T06:52:00Z",
    "title": "Quarterly Secret Rotation - Staging DB",
    "body": "Due today 17:00 IST. Assigned to Ganesh Nair. Requires updating Vault/SSM and restarting staging API pods."
  },
  {
    "id": "alert-016",
    "source": "Slack",
    "sender": "security-officer",
    "timestamp": "2026-10-23T07:10:00Z",
    "title": "Reminder: Staging DB Secret Rotation",
    "body": "Just making sure this is on radar for before 5 PM to prevent staging pipeline disruptions."
  },
  {
    "id": "alert-017",
    "source": "Datadog",
    "sender": "Monitors",
    "timestamp": "2026-10-23T07:15:00Z",
    "title": "[Info] Daily database backup completed",
    "body": "Snapshot snapshot-prod-db-2026-10-23 created successfully. Size: 412 GB. Status: Available."
  },
  {
    "id": "alert-018",
    "source": "PagerDuty",
    "sender": "AlertBot",
    "timestamp": "2026-10-23T07:20:00Z",
    "title": "[Info] Daily on-call handoff scheduled for 10:00 AM",
    "body": "Primary on-call rotation handoff: Alex -> Ganesh. Review active alerts before handoff."
  },
  {
    "id": "alert-019",
    "source": "Slack",
    "sender": "devops-chat",
    "timestamp": "2026-10-23T07:25:00Z",
    "title": "Morning standup cancelled today",
    "body": "Friendly reminder: no morning standup today due to executive planning offsite. Post async updates in thread."
  },
  {
    "id": "alert-020",
    "source": "CloudWatch",
    "sender": "aws-sns-alerts",
    "timestamp": "2026-10-23T07:30:00Z",
    "title": "ALARM: BillingForecastThresholdExceeded",
    "body": "Current month forecast ($4,850) is approaching budget limit ($5,000). Review unattached EBS volumes."
  },
  {
    "id": "alert-021",
    "source": "Email",
    "sender": "FinOps Bot <finops@company.com>",
    "timestamp": "2026-10-23T07:32:00Z",
    "title": "Action: Clean up 14 orphaned EBS volumes",
    "body": "We identified 14 unattached gp3 EBS volumes in us-east-1 totaling 1.2 TB costing $96/month. Please delete unneeded snapshots/volumes."
  },
  {
    "id": "alert-022",
    "source": "Slack",
    "sender": "alex.sre",
    "timestamp": "2026-10-23T07:35:00Z",
    "title": "Ready for on-call handoff?",
    "body": "Hey Ganesh, everything is quiet in prod right now after the early morning Redis failover. Ready for handoff at 10?"
  }
],
  maintainer_backlog: [
  {
    "id": "gh-001",
    "source": "GitHub",
    "sender": "contributor-42",
    "timestamp": "2026-10-23T01:00:00Z",
    "title": "Issue #810: Memory leak in WebSocket connection pool",
    "body": "When clients disconnect abruptly without FIN handshake, connection object remains in _active_sockets dict. Reproducible in production with 10k connections."
  },
  {
    "id": "gh-002",
    "source": "GitHub",
    "sender": "contributor-42",
    "timestamp": "2026-10-23T01:05:00Z",
    "title": "PR #812: Fix memory leak in WebSocket connection pool",
    "body": "Fixes #810. Added weakref callback and explicit cleanup on transport close. Added regression test verifying garbage collection."
  },
  {
    "id": "gh-003",
    "source": "GitHub",
    "sender": "coderabbitai[bot]",
    "timestamp": "2026-10-23T01:08:00Z",
    "title": "CodeRabbit Review on PR #812",
    "body": "Walkthrough: PR #812 properly frees orphaned socket references. 1 minor suggestion: add docstring to _cleanup_ref(). Merge risk: Low."
  },
  {
    "id": "gh-004",
    "source": "GitHub",
    "sender": "newbie-dev",
    "timestamp": "2026-10-23T01:15:00Z",
    "title": "Can I work on #810?",
    "body": "Hey maintainers! I'd like to work on issue #810 for Hacktoberfest. Please assign me."
  },
  {
    "id": "gh-005",
    "source": "GitHub",
    "sender": "another-student",
    "timestamp": "2026-10-23T01:20:00Z",
    "title": "Assign me #810 please",
    "body": "Interested in fixing #810. Please assign to me!"
  },
  {
    "id": "gh-006",
    "source": "GitHub",
    "sender": "spam-bot-88",
    "timestamp": "2026-10-23T01:25:00Z",
    "title": "PR #813: Fix typos in README.md",
    "body": "Fixed spelling of 'implementation' and added Hacktoberfest badge to README."
  },
  {
    "id": "gh-007",
    "source": "GitHub",
    "sender": "spam-bot-89",
    "timestamp": "2026-10-23T01:28:00Z",
    "title": "PR #814: Update README.md formatting",
    "body": "Added trailing newline and fixed markdown list spacing."
  },
  {
    "id": "gh-008",
    "source": "GitHub",
    "sender": "security-researcher-x",
    "timestamp": "2026-10-23T02:00:00Z",
    "title": "CRITICAL SECURITY ADVISORY (Private): Remote Code Execution in config parser",
    "body": "Discovered unsafe yaml.load() call in server/config.py:44 instead of yaml.safe_load(). Attackers can supply custom tags in config upload to execute arbitrary python code. Exploit PoC attached."
  },
  {
    "id": "gh-009",
    "source": "Email",
    "sender": "security-researcher-x <research@infosec.org>",
    "timestamp": "2026-10-23T02:05:00Z",
    "title": "URGENT Security Vulnerability Disclosure - YAML RCE",
    "body": "Sent this via GitHub Security Advisory as well. Please acknowledge receipt within 48 hours. Ready to coordinate patch release."
  },
  {
    "id": "gh-010",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T02:10:00Z",
    "title": "Nightly release build failed",
    "body": "Nightly build matrix failed on Windows Python 3.13: ImportError: DLL load failed while importing _sqlite3."
  },
  {
    "id": "gh-011",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T02:15:00Z",
    "title": "Scheduled security scan: 0 new vulnerabilities found",
    "body": "Trivy container scan complete. 0 critical, 0 high."
  },
  {
    "id": "gh-012",
    "source": "Discord",
    "sender": "community-user",
    "timestamp": "2026-10-23T02:20:00Z",
    "title": "Help with installation on Windows",
    "body": "Getting 'poetry not found' error during setup. Anyone online to help?"
  },
  {
    "id": "gh-013",
    "source": "Discord",
    "sender": "community-user",
    "timestamp": "2026-10-23T02:30:00Z",
    "title": "Nevermind figured it out!",
    "body": "Had to add python scripts to PATH. All good now."
  },
  {
    "id": "gh-014",
    "source": "GitHub",
    "sender": "dependabot[bot]",
    "timestamp": "2026-10-23T03:00:00Z",
    "title": "Bump fastapi from 0.115.0 to 0.115.2",
    "body": "Bumps fastapi to latest patch release. All tests pass."
  },
  {
    "id": "gh-015",
    "source": "GitHub",
    "sender": "dependabot[bot]",
    "timestamp": "2026-10-23T03:02:00Z",
    "title": "Bump pydantic from 2.9.1 to 2.9.2",
    "body": "Bumps pydantic to latest patch release. All tests pass."
  },
  {
    "id": "gh-016",
    "source": "GitHub",
    "sender": "contributor-42",
    "timestamp": "2026-10-23T03:10:00Z",
    "title": "Friendly ping on PR #812 review",
    "body": "CI passed and CodeRabbit suggestions incorporated. Ready for maintainer merge whenever you have a moment!"
  },
  {
    "id": "gh-017",
    "source": "GitHub",
    "sender": "stale-bot",
    "timestamp": "2026-10-23T03:30:00Z",
    "title": "Closed inactive PR #750",
    "body": "PR #750 closed due to 30 days of inactivity."
  },
  {
    "id": "gh-018",
    "source": "GitHub",
    "sender": "stale-bot",
    "timestamp": "2026-10-23T03:32:00Z",
    "title": "Closed inactive PR #751",
    "body": "PR #751 closed due to 30 days of inactivity."
  },
  {
    "id": "gh-019",
    "source": "GitHub",
    "sender": "enterprise-sponsor",
    "timestamp": "2026-10-23T04:00:00Z",
    "title": "New GitHub Sponsor: Acme Corp ($250/mo)",
    "body": "Acme Corp has sponsored your open-source work at the Enterprise tier. Note: Thank you for building such reliable tools!"
  },
  {
    "id": "gh-020",
    "source": "Email",
    "sender": "GitHub Sponsors <sponsors@github.com>",
    "timestamp": "2026-10-23T04:02:00Z",
    "title": "You received a new sponsor pledge",
    "body": "Acme Corp is now sponsoring you for $250.00/month."
  },
  {
    "id": "gh-021",
    "source": "GitHub",
    "sender": "dev-advocate",
    "timestamp": "2026-10-23T04:30:00Z",
    "title": "Invitation: Present at Open Source Summit 2026",
    "body": "Hi Ganesh, we'd love to invite you to give a 20-minute lightning talk on local AI agents at OSS Summit. Speaker confirmation deadline is October 28."
  },
  {
    "id": "gh-022",
    "source": "Email",
    "sender": "Conference Chair <chair@ossummit.org>",
    "timestamp": "2026-10-23T04:35:00Z",
    "title": "OSS Summit Speaker Invitation Confirmation Needed by Oct 28",
    "body": "Following up on the GitHub message: please confirm your speaking availability and submit your talk title by October 28."
  },
  {
    "id": "gh-023",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:00:00Z",
    "title": "Feature request: Add Dark Mode toggle to documentation",
    "body": "The docs are currently light mode only. Can we add a dark mode toggle using VitePress or Starlight?"
  },
  {
    "id": "gh-024",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:05:00Z",
    "title": "+1 on Dark Mode docs",
    "body": "Agree, reading docs at night hurts eyes."
  },
  {
    "id": "gh-025",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:10:00Z",
    "title": "+1 on Dark Mode",
    "body": "Would love this!"
  },
  {
    "id": "gh-026",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:15:00Z",
    "title": "+1",
    "body": "+1"
  },
  {
    "id": "gh-027",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:20:00Z",
    "title": "+1",
    "body": "+1"
  },
  {
    "id": "gh-028",
    "source": "GitHub",
    "sender": "user-feedback",
    "timestamp": "2026-10-23T05:25:00Z",
    "title": "PR #815: Add dark mode toggle to docs",
    "body": "Implemented theme toggle in docs navbar with localStorage persistence. Closes #823."
  },
  {
    "id": "gh-029",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T05:28:00Z",
    "title": "Docs build passed for PR #815",
    "body": "Preview deployment available at https://preview-815.example.com."
  },
  {
    "id": "gh-030",
    "source": "GitHub",
    "sender": "package-tracker",
    "timestamp": "2026-10-23T05:40:00Z",
    "title": "PyPI monthly downloads crossed 50,000!",
    "body": "Congratulations, your package reached 52,140 downloads this month on PyPI."
  },
  {
    "id": "gh-031",
    "source": "GitHub",
    "sender": "user-question",
    "timestamp": "2026-10-23T06:00:00Z",
    "title": "Discussion: Does this support Python 3.14 alpha?",
    "body": "Testing against 3.14-dev and seeing Cython compilation warning. Is 3.14 officially supported?"
  },
  {
    "id": "gh-032",
    "source": "GitHub",
    "sender": "contributor-pro",
    "timestamp": "2026-10-23T06:15:00Z",
    "title": "Answered discussion: Does this support Python 3.14 alpha?",
    "body": "Python 3.14 is currently pre-alpha; official support is targeted for next quarter once free-threaded CPython stabilizes."
  },
  {
    "id": "gh-033",
    "source": "GitHub",
    "sender": "github-actions[bot]",
    "timestamp": "2026-10-23T06:30:00Z",
    "title": "CodeQL analysis passed: 0 alerts",
    "body": "Static analysis check finished on main branch."
  },
  {
    "id": "gh-034",
    "source": "Email",
    "sender": "GitHub Notifications <notifications@github.com>",
    "timestamp": "2026-10-23T06:45:00Z",
    "title": "Daily digest: 18 unread notifications in repository",
    "body": "You have 18 unread notifications across 6 threads in your starred and watched repositories."
  },
  {
    "id": "gh-035",
    "source": "GitHub",
    "sender": "security-researcher-x",
    "timestamp": "2026-10-23T07:00:00Z",
    "title": "PR #816: Fix YAML safe_load vulnerability (Security Hotfix)",
    "body": "Draft PR addressing the private vulnerability disclosure: replaces yaml.load with yaml.safe_load and disallows dangerous custom constructors. Ready for maintainer review."
  }
],
};

export const EMBEDDED_BENCHMARKS: BenchmarkMetrics[] = [
  {
    dataset_name: 'Chaotic Monday Morning',
    raw_message_count: 28,
    duplicate_clusters_found: 3,
    noise_items_filtered: 4,
    volume_reduction_pct: 89.3,
    cognitive_load_reduction_pct: 89.3,
    priority_action_count: 3,
    confirmed_deadlines_count: 1,
    inferred_deadlines_count: 0,
    execution_latency_ms: 55.16,
    model_runtime: 'rule-based-fallback (Ollama Gemma bridge standby)',
  },
  {
    dataset_name: 'DevOps Alert Storm',
    raw_message_count: 22,
    duplicate_clusters_found: 4,
    noise_items_filtered: 1,
    volume_reduction_pct: 86.4,
    cognitive_load_reduction_pct: 86.4,
    priority_action_count: 3,
    confirmed_deadlines_count: 0,
    inferred_deadlines_count: 0,
    execution_latency_ms: 18.11,
    model_runtime: 'rule-based-fallback (Ollama Gemma bridge standby)',
  },
  {
    dataset_name: 'Maintainer Backlog',
    raw_message_count: 35,
    duplicate_clusters_found: 5,
    noise_items_filtered: 6,
    volume_reduction_pct: 91.4,
    cognitive_load_reduction_pct: 91.4,
    priority_action_count: 3,
    confirmed_deadlines_count: 0,
    inferred_deadlines_count: 0,
    execution_latency_ms: 44.78,
    model_runtime: 'rule-based-fallback (Ollama Gemma bridge standby)',
  },
];
