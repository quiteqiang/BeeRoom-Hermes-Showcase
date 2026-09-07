import { useEffect, useState } from "react";
import { apiGet, apiPost, type Comment } from "../api";

export function ReviewQueuePage({ className, onClassChange }: { className: string; onClassChange: (value: string) => void }) {
  const [items, setItems] = useState<Comment[]>([]);
  const [message, setMessage] = useState("");

  function load() {
    const suffix = className ? `?class_name=${encodeURIComponent(className)}` : "";
    apiGet<Comment[]>(`/api/comments/review-queue${suffix}`).then(setItems).catch(() => setItems([]));
  }

  useEffect(() => { load(); }, [className]);

  async function approve(id: string) {
    await apiPost(`/api/comments/${id}/approve`);
    setMessage("已批准");
    load();
  }

  async function reject(id: string) {
    await apiPost(`/api/comments/${id}/reject`);
    setMessage("已拒绝");
    load();
  }

  return (
    <main>
      <h1>Review Queue</h1>
      <label>班级筛选<input value={className} onChange={(event) => onClassChange(event.target.value)} /></label>
      {message ? <p role="status">{message}</p> : null}
      {items.map((item) => (
        <article key={item.id}>
          <header><strong>{item.category}</strong> · {item.comment_date}{item.topic ? ` · ${item.topic}` : ""}</header>
          <p>{item.text}</p>
          <p>证据：{item.evidence}</p>
          {item.source_span ? <p>来源：{item.source_span}</p> : null}
          <button type="button" onClick={() => approve(item.id)}>Approve</button>
          <button type="button" onClick={() => reject(item.id)}>Reject</button>
        </article>
      ))}
    </main>
  );
}
