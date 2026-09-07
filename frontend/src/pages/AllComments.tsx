import { useEffect, useState } from "react";
import { apiGet, type Comment, type Student } from "../api";

const statusLabels: Record<string, string> = {
  pending_review: "待审核",
  approved: "已批准",
  edited: "已编辑",
  rejected: "已拒绝",
};

export function AllCommentsPage({ students }: { students: Student[] }) {
  const [items, setItems] = useState<Comment[]>([]);
  const [className, setClassName] = useState("");
  const [reviewStatus, setReviewStatus] = useState("");
  const [category, setCategory] = useState("");
  const [message, setMessage] = useState("");

  function load() {
    const params = new URLSearchParams();
    if (className) params.set("class_name", className);
    if (reviewStatus) params.set("review_status", reviewStatus);
    if (category) params.set("category", category);
    const suffix = params.toString() ? `?${params.toString()}` : "";
    apiGet<Comment[]>(`/api/comments${suffix}`)
      .then((result) => {
        setItems(result);
        setMessage("");
      })
      .catch(() => {
        setItems([]);
        setMessage("评语加载失败");
      });
  }

  useEffect(() => {
    load();
  }, [className, reviewStatus, category]);

  const studentsById = new Map(students.map((student) => [student.id, student]));

  return (
    <main>
      <h1>All Comments</h1>
      <label>班级筛选<input value={className} onChange={(event) => setClassName(event.target.value)} /></label>
      <label>
        审核状态
        <select value={reviewStatus} onChange={(event) => setReviewStatus(event.target.value)}>
          <option value="">全部</option>
          <option value="pending_review">待审核</option>
          <option value="approved">已批准</option>
          <option value="edited">已编辑</option>
          <option value="rejected">已拒绝</option>
        </select>
      </label>
      <label>
        类别
        <select value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="">全部</option>
          <option value="learning">学习</option>
          <option value="behaviour">行为</option>
          <option value="interaction">互动</option>
          <option value="encouragement">鼓励</option>
          <option value="general">综合</option>
          <option value="whole_class">全班</option>
          <option value="needs_review">需审核</option>
        </select>
      </label>
      {message ? <p role="status">{message}</p> : null}
      {items.length === 0 && !message ? <p>暂无评语</p> : null}
      {items.map((item) => {
        const student = item.student_id ? studentsById.get(item.student_id) : undefined;
        const studentLabel = student ? `${student.display_name} · ${student.class_name}` : "未分配学生";
        return (
          <article key={item.id}>
            <header>
              <strong>{studentLabel}</strong> · {item.comment_date} · {statusLabels[item.review_status] ?? item.review_status}
              {item.topic ? ` · ${item.topic}` : ""}
            </header>
            <p>类别：{item.category}</p>
            <p>{item.text}</p>
            <p>证据：{item.evidence}</p>
            {item.source_span ? <p>来源：{item.source_span}</p> : null}
          </article>
        );
      })}
    </main>
  );
}
