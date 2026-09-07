export async function apiGet<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`GET ${url} failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export async function apiPost<T>(url: string, body?: unknown): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`POST ${url} failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export interface Student {
  id: string;
  display_name: string;
  student_code: string;
  class_name: string;
  year_level: number;
  aliases: string[];
  active: boolean;
}

export interface Comment {
  id: string;
  student_id: string | null;
  comment_date: string;
  topic: string | null;
  category: string;
  text: string;
  evidence: string;
  source_span: string | null;
  confidence: number;
  review_status: string;
}
