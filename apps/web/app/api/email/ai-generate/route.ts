import { NextRequest, NextResponse } from "next/server";
import { AIGenerateEmailSchema } from "@/lib/validators/email";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const validation = AIGenerateEmailSchema.safeParse(body);

    if (!validation.success) {
      return NextResponse.json(
        { success: false, errors: validation.error.flatten().fieldErrors },
        { status: 400 }
      );
    }

    const { company, industry, decisionMaker, painPoints, interestedService, country, previousCommunication } = validation.data;

    const recipientName = decisionMaker || "Team";
    const painText = painPoints ? `addressing challenges like ${painPoints}` : "building scalable cloud solutions";
    const countryText = country ? ` in ${country}` : "";

    const generatedSubject = `Personalized Technology Partnership for ${company}: ${interestedService}`;

    const generatedHtml = `<p>Hi ${recipientName},</p>

<p>I hope this email finds you well. I've been following <strong>${company}</strong>'s work in the ${industry} space${countryText} and wanted to reach out directly.</p>

<p>At <strong>Axorks</strong>, we specialize in high-impact engineering solutions, specifically focusing on <strong>${interestedService}</strong>. We routinely partner with ambitious growth companies to solve technical bottlenecks, particularly around ${painText}.</p>

${previousCommunication ? `<p><em>Reflecting on our prior discussions (${previousCommunication}), we have updated our deployment frameworks to offer even faster turnaround times.</em></p>` : ""}

<p>Here is what a collaboration with Axorks delivers:</p>
<ul>
  <li>Dedicated Staffing & Enterprise-grade Code Quality</li>
  <li>Rapid 2-Week Prototyping & CI/CD Pipelines</li>
  <li>Full Security Compliance & Modern Next.js / Cloud Architecture</li>
</ul>

<p>Would you be open to a 15-minute discovery call next week to explore how we can support ${company}'s current software roadmap?</p>

<p>Best regards,<br/>
<strong>Engineering Leadership | Axorks</strong><br/>
<a href="mailto:hello@axorks.com">hello@axorks.com</a></p>`;

    return NextResponse.json({
      success: true,
      subject: generatedSubject,
      html: generatedHtml,
    });
  } catch (error: any) {
    console.error("Error in /api/email/ai-generate:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to generate AI email" },
      { status: 500 }
    );
  }
}
