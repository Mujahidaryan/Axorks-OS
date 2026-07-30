export interface EmailTemplate {
  id: string;
  name: string;
  category: "sales" | "projects" | "finance" | "support" | "general";
  subject: string;
  description: string;
  html: string;
}

export const EMAIL_TEMPLATES: EmailTemplate[] = [
  {
    id: "cold-outreach",
    name: "Cold Outreach",
    category: "sales",
    subject: "Scaling {{company}}'s software infrastructure with Axorks",
    description: "Personalized cold outreach template for target decision makers.",
    html: `<p>Hi {{decision_maker}},</p>
<p>I hope this email finds you well. I was following {{company}}'s growth in the {{industry}} space and was really impressed by your recent milestones.</p>
<p>At <strong>Axorks</strong>, we partner with growing tech organizations to design, build, and scale high-performance web and mobile applications.</p>
<p>We've helped software consultancies and tech brands solve critical engineering bottlenecks, including:</p>
<ul>
  <li>Custom Cloud & SaaS Product Development</li>
  <li>AI Infrastructure & Workflow Automation</li>
  <li>Legacy Code Modernization & API Integration</li>
</ul>
<p>Would you be open to a quick 15-minute intro call next Tuesday to explore if there's alignment?</p>
<p>Best regards,<br/><strong>The Axorks Team</strong><br/>hello@axorks.com</p>`
  },
  {
    id: "proposal",
    name: "Proposal",
    category: "sales",
    subject: "Project Proposal & Scope of Work for {{company}}",
    description: "Formal proposal presentation email with attached proposal document.",
    html: `<p>Dear {{decision_maker}},</p>
<p>Thank you for taking the time to discuss {{company}}'s upcoming software initiative with us.</p>
<p>We have synthesized your technical requirements into a comprehensive <strong>Project Proposal & Scope of Work</strong>. The detailed document is attached to this email for your review.</p>
<p><strong>Executive Summary Highlights:</strong></p>
<ul>
  <li>Architecture & Technology Stack Strategy</li>
  <li>Phased Sprint Breakdown & Milestones</li>
  <li>Deliverables, SLA, and Investment Breakdown</li>
</ul>
<p>Please let us know if you would like to schedule a walk-through call to discuss the proposal details.</p>
<p>Warm regards,<br/><strong>Axorks Solutions Team</strong></p>`
  },
  {
    id: "quotation",
    name: "Quotation",
    category: "sales",
    subject: "Official Quotation #QT-{{quote_number}} for {{company}}",
    description: "Itemized cost estimate and pricing quotation delivery.",
    html: `<p>Hi {{decision_maker}},</p>
<p>Following our recent discovery session, please find attached the official cost quotation <strong>#QT-{{quote_number}}</strong> for your project.</p>
<p>This quotation is valid for 30 days from today and includes all development, quality assurance, and initial cloud deployment setup.</p>
<p>If you have any questions regarding line items or payment terms, feel free to reply directly to this email.</p>
<p>Best regards,<br/><strong>Axorks Finance & Accounts</strong></p>`
  },
  {
    id: "meeting-request",
    name: "Meeting Request",
    category: "sales",
    subject: "Meeting Invitation: Axorks & {{company}} Technical Alignment",
    description: "Request for calendar scheduling and discovery call.",
    html: `<p>Hi {{decision_maker}},</p>
<p>We would love to get a 30-minute discovery call on the calendar to discuss {{company}}'s software requirements in detail.</p>
<p>Please let us know which of the following times works best for you (or share your preferred calendar link):</p>
<ul>
  <li>Option 1: Tuesday at 10:00 AM EST</li>
  <li>Option 2: Wednesday at 2:00 PM EST</li>
  <li>Option 3: Thursday at 11:30 AM EST</li>
</ul>
<p>Looking forward to speaking with you!</p>
<p>Best regards,<br/><strong>Axorks Team</strong></p>`
  },
  {
    id: "follow-up",
    name: "Follow-up",
    category: "sales",
    subject: "Following up on our conversation — {{company}}",
    description: "Polite check-in follow up for pending leads.",
    html: `<p>Hi {{decision_maker}},</p>
<p>I wanted to quickly follow up on my previous message regarding {{company}}'s technical roadmap.</p>
<p>I understand things get busy. If you're still looking into solving {{pain_point}}, I'd be glad to share how our engineering team recently addressed a similar challenge for another client.</p>
<p>Shall we connect for 10 minutes later this week?</p>
<p>Best regards,<br/><strong>Axorks Sales Team</strong></p>`
  },
  {
    id: "project-kickoff",
    name: "Project Kickoff",
    category: "projects",
    subject: "🚀 Project Kickoff: Welcome to Axorks OS — {{project_name}}",
    description: "Onboarding email sent at project inception.",
    html: `<p>Dear {{company}} Team,</p>
<p>We are thrilled to officially launch the <strong>{{project_name}}</strong> project!</p>
<p>Our engineering leads have set up your dedicated workspace in <strong>Axorks OS</strong>. You can log into your Client Portal to track real-time progress, view sprint backlogs, and share assets.</p>
<p><strong>Next Steps:</strong></p>
<ul>
  <li>Kickoff Meeting: {{kickoff_date}}</li>
  <li>Client Portal Credentials Sent</li>
  <li>First Sprint Planning Commences</li>
</ul>
<p>Welcome aboard!</p>
<p>Best regards,<br/><strong>Axorks Project Management Office</strong></p>`
  },
  {
    id: "project-delivery",
    name: "Project Delivery",
    category: "projects",
    subject: "🎉 Milestone Handover: {{project_name}} is Ready for Review",
    description: "Delivery notice for project milestone or final release.",
    html: `<p>Hi {{decision_maker}},</p>
<p>We are excited to inform you that milestone <strong>{{milestone_title}}</strong> for <strong>{{project_name}}</strong> has been successfully built, tested, and deployed to staging.</p>
<p>Please review the release notes attached and test the build at your earliest convenience.</p>
<p>Thank you for your ongoing partnership!</p>
<p>Best regards,<br/><strong>Axorks Engineering Team</strong></p>`
  },
  {
    id: "invoice",
    name: "Invoice",
    category: "finance",
    subject: "Invoice #INV-{{invoice_number}} from Axorks Inc.",
    description: "Billing notice with payment link and attached PDF invoice.",
    html: `<p>Hi {{decision_maker}},</p>
<p>Please find attached Invoice <strong>#INV-{{invoice_number}}</strong> for services rendered on <strong>{{project_name}}</strong>.</p>
<p><strong>Invoice Summary:</strong></p>
<ul>
  <li>Invoice Date: {{invoice_date}}</li>
  <li>Amount Due: {{amount_due}}</li>
  <li>Due Date: {{due_date}}</li>
</ul>
<p>You can pay securely online via credit card or bank transfer through your Axorks Client Portal.</p>
<p>Thank you for your prompt payment!</p>
<p>Best regards,<br/><strong>Axorks Billing Department</strong></p>`
  },
  {
    id: "maintenance-reminder",
    name: "Maintenance Reminder",
    category: "support",
    subject: "Upcoming Scheduled Maintenance Notice — {{system_name}}",
    description: "Notification for planned maintenance window.",
    html: `<p>Dear {{company}} Team,</p>
<p>Please be advised that we have scheduled routine system maintenance for <strong>{{system_name}}</strong> on <strong>{{maintenance_date}}</strong> between {{start_time}} and {{end_time}}.</p>
<p>During this window, brief service interruptions may occur as we deploy critical security patches and performance optimizations.</p>
<p>If you have any questions or urgent requests, please contact our support desk.</p>
<p>Best regards,<br/><strong>Axorks DevOps & Security Operations</strong></p>`
  },
  {
    id: "thank-you",
    name: "Thank You",
    category: "general",
    subject: "Thank you for partnering with Axorks",
    description: "Appreciation message for clients after project completion.",
    html: `<p>Dear {{decision_maker}},</p>
<p>On behalf of the entire team at Axorks, I wanted to express our sincere gratitude for choosing us as your technology partner for {{project_name}}.</p>
<p>It has been a privilege working with your team, and we look forward to supporting your future growth and tech roadmap.</p>
<p>Warmest regards,<br/><strong>Leadership Team, Axorks</strong></p>`
  },
  {
    id: "general-inquiry",
    name: "General Inquiry",
    category: "general",
    subject: "Response regarding your inquiry to Axorks",
    description: "Standard response template for general customer inquiries.",
    html: `<p>Hi {{contact_name}},</p>
<p>Thank you for reaching out to Axorks!</p>
<p>We received your inquiry regarding <em>"{{inquiry_topic}}"</em> and an account specialist has been assigned to your request.</p>
<p>We will follow up with detailed information within 24 business hours.</p>
<p>Best regards,<br/><strong>Axorks Client Support</strong></p>`
  }
];
