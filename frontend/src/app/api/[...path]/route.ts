import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.BACKEND_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `${API_BASE}/${path.join("/")}`;
  const searchParams = request.nextUrl.searchParams.toString();
  const fullUrl = searchParams ? `${url}?${searchParams}` : url;

  try {
    const res = await fetch(fullUrl, {
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: "Failed to fetch" }, { status: 502 });
  }
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `${API_BASE}/${path.join("/")}`;
  const body = await request.text();

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: "Failed to fetch" }, { status: 502 });
  }
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `${API_BASE}/${path.join("/")}`;
  const body = await request.text();

  try {
    const res = await fetch(url, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body,
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: "Failed to fetch" }, { status: 502 });
  }
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `${API_BASE}/${path.join("/")}`;

  try {
    const res = await fetch(url, { method: "DELETE" });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: "Failed to fetch" }, { status: 502 });
  }
}
