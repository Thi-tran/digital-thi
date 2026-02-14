import { NextRequest, NextResponse } from 'next/server';

interface ChatRequest {
  message: string;
}

interface ChatResponse {
  success: boolean;
  data?: {
    response: string;
  };
  error?: string;
}

export async function POST(
  request: NextRequest
): Promise<NextResponse<ChatResponse>> {
  try {
    const body: ChatRequest = await request.json();
    const { message } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { success: false, error: 'Message is required' },
        { status: 400 }
      );
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

    const response = await fetch(`${backendUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const data = await response.json();

    return NextResponse.json(
      { success: true, data },
      { status: 200 }
    );
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to process chat message' },
      { status: 500 }
    );
  }
}
