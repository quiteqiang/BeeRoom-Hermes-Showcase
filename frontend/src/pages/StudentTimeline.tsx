import { useEffect, useState } from "react";
import { apiGet, type Comment, type Student } from "../api";

const statusLabels: Record<string, string> = {
  pending_review: "待审核",
  approved: "已批准",
  edited: "已编辑",
  rejected: "已拒绝",
};

export function StudentTimelinePage({ studentId, students, onStudentChange }: { studentId: string; students: Student[]; onStudentChange: (id: string) => void }) {
  const [items, setItems] = useState<Comment[]>([]);

  useEffect(() => {
    if (!studentId) {
      setItems([]);
      return;
    }
    apiGet<Comment[]>(`/api/students/${studentId}/comments`).then(setItems).catch(() => setItems([]));
  }, [studentId]);

  return (
    <main>
      <h1>Student Timeline</h1>
      <label>
        学生
        <select value={studentId} onChange={(event) => onStudentChange(event.target.value)}>
          <option value="">选择学生</option>
          {students.map((student) => <option key={student.id} value={student.id}>{student.display_name}（{student.class_name}）</option>)}
        </select>
      </label>
      {items.map((item) => (
        <article key={item.id}>
          <header><strong>{item.category}</strong> · {item.comment_date} · {statusLabels[item.review_status] ?? item.review_status}{item.topic ? ` · ${item.topic}` : ""}</header>
          <p>{item.text}</p>
          <p>证据：{item.evidence}</p>
          {item.source_span ? <p>来源：{item.source_span}</p> : null}
        </article>
      ))}
    </main>
  );
}
