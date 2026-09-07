import { useState } from "react";
import { apiPost, type Student } from "../api";

type Props = {
  students: Student[];
  studentId: string;
  onStudentChange: (id: string) => void;
  className: string;
  onClassChange: (value: string) => void;
};

export function TodayPage({ students, studentId, onStudentChange, className, onClassChange }: Props) {
  const [commentDate, setCommentDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [topic, setTopic] = useState("");
  const [text, setText] = useState("");
  const [message, setMessage] = useState("");

  async function submitText() {
    try {
      const result = await apiPost<unknown[]>("/api/comments/ingest-text", {
        class_name: className || undefined,
        comment_date: commentDate,
        topic: topic || undefined,
        text,
      });
      setMessage(`已生成 ${result.length} 条待审核评语`);
      setText("");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "提交失败");
    }
  }

  return (
    <main>
      <h1>Today</h1>
      <label>班级（可选）<input value={className} onChange={(event) => onClassChange(event.target.value)} placeholder="Example Class" /></label>
      <label>
        学生时间线
        <select value={studentId} onChange={(event) => onStudentChange(event.target.value)}>
          <option value="">选择学生</option>
          {students.map((student) => <option key={student.id} value={student.id}>{student.display_name}（{student.class_name}）</option>)}
        </select>
      </label>
      <label>日期<input type="date" value={commentDate} onChange={(event) => setCommentDate(event.target.value)} /></label>
      <label>主题<input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="如：对称" /></label>
      <label>
        课堂记录（可粘贴转写文本）
        <textarea rows={6} value={text} onChange={(event) => setText(event.target.value)} placeholder="Student A: understood the activity. Student B: helped a classmate." />
      </label>
      <button type="button" onClick={submitText} disabled={!text.trim()}>生成待审核评语</button>
      {message ? <p role="status">{message}</p> : null}
    </main>
  );
}
