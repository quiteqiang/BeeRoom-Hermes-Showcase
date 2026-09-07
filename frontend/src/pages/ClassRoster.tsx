import { useState } from "react";
import { apiPost, type Student } from "../api";

export function ClassRosterPage({
  students,
  onStudentsChange,
}: {
  students: Student[];
  onStudentsChange: () => void;
}) {
  const [displayName, setDisplayName] = useState("");
  const [studentCode, setStudentCode] = useState("");
  const [className, setClassName] = useState("");
  const [yearLevel, setYearLevel] = useState("1");
  const [aliases, setAliases] = useState("");
  const [message, setMessage] = useState("");

  async function addStudent() {
    try {
      await apiPost("/api/students", {
        display_name: displayName,
        student_code: studentCode,
        class_name: className,
        year_level: Number(yearLevel),
        aliases: aliases.split(/[,，]/).map((item) => item.trim()).filter(Boolean),
      });
      setDisplayName("");
      setStudentCode("");
      setAliases("");
      setMessage("学生已添加");
      onStudentsChange();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "添加失败");
    }
  }

  return (
    <main>
      <h1>Students</h1>
      <label>姓名<input value={displayName} onChange={(event) => setDisplayName(event.target.value)} /></label>
      <label>学号<input value={studentCode} onChange={(event) => setStudentCode(event.target.value)} /></label>
      <label>班级<input value={className} onChange={(event) => setClassName(event.target.value)} placeholder="Example Class" /></label>
      <label>
        年级
        <select value={yearLevel} onChange={(event) => setYearLevel(event.target.value)}>
          {[1, 2, 3, 4, 5].map((level) => <option key={level} value={level}>{level} 年级</option>)}
        </select>
      </label>
      <label>别名（逗号分隔）<input value={aliases} onChange={(event) => setAliases(event.target.value)} /></label>
      <button type="button" onClick={addStudent} disabled={!displayName.trim() || !studentCode.trim() || !className.trim()}>
        添加学生
      </button>
      {message ? <p role="status">{message}</p> : null}
      <h2>全部学生</h2>
      {students.length === 0 ? <p>暂无学生</p> : null}
      {students.map((student) => (
        <article key={student.id}>
          <h3>{student.display_name}</h3>
          <p>学号：{student.student_code}</p>
          <p>班级：{student.class_name}</p>
          <p>年级：{student.year_level} 年级</p>
          <p>别名：{student.aliases.length ? student.aliases.join("、") : "无"}</p>
          <p>状态：{student.active ? "在读" : "停用"}</p>
        </article>
      ))}
    </main>
  );
}
