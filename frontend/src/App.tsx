import { useEffect, useState } from "react";
import { apiGet, type Student } from "./api";
import { AllCommentsPage } from "./pages/AllComments";
import { ClassRosterPage } from "./pages/ClassRoster";
import { ReviewQueuePage } from "./pages/ReviewQueue";
import { StudentTimelinePage } from "./pages/StudentTimeline";
import { TodayPage } from "./pages/Today";

type Tab = "today" | "roster" | "comments" | "review" | "timeline";

export default function App() {
  const [tab, setTab] = useState<Tab>("today");
  const [students, setStudents] = useState<Student[]>([]);
  const [studentId, setStudentId] = useState("");
  const [className, setClassName] = useState("");

  function refreshStudents() {
    apiGet<Student[]>("/api/students").then(setStudents).catch(() => setStudents([]));
  }

  useEffect(() => {
    refreshStudents();
  }, []);

  return (
    <div>
      <nav>
        <button type="button" onClick={() => setTab("today")}>Today</button>
        <button type="button" onClick={() => setTab("roster")}>Students</button>
        <button type="button" onClick={() => setTab("comments")}>All Comments</button>
        <button type="button" onClick={() => setTab("review")}>Review Queue</button>
        <button type="button" onClick={() => setTab("timeline")}>Timeline</button>
      </nav>
      {tab === "today" ? (
        <TodayPage
          students={students}
          studentId={studentId}
          onStudentChange={setStudentId}
          className={className}
          onClassChange={setClassName}
        />
      ) : null}
      {tab === "roster" ? <ClassRosterPage students={students} onStudentsChange={refreshStudents} /> : null}
      {tab === "comments" ? <AllCommentsPage students={students} /> : null}
      {tab === "review" ? <ReviewQueuePage className={className} onClassChange={setClassName} /> : null}
      {tab === "timeline" ? (
        <StudentTimelinePage studentId={studentId} students={students} onStudentChange={setStudentId} />
      ) : null}
    </div>
  );
}
