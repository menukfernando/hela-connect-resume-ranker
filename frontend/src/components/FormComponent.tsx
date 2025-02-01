import React, { useState } from "react";

export interface IResults {
  rank: number;
  name: string;
  email: string;
  similarity: number;
}

interface FormComponentProps {
  onResults: (results: IResults[]) => void;
}

const FormComponent = ({ onResults }: FormComponentProps) => {
  const [jobDescription, setJobDescription] = useState<string>(
    `Software Engineer - Full Stack

About the Role
We are looking for a Full Stack Software Engineer to join our growing engineering team. As a Full Stack Engineer, you will design, develop, and maintain scalable web applications, contributing to both frontend and backend codebases. You will collaborate with product managers, designers, and other engineers to deliver high-quality features in a fast-paced environment.

Key Responsibilities
- Design, develop, and deploy web applications with a focus on scalability and performance.
- Build and maintain backend services using Node.js, Python, or similar technologies.
- Develop user interfaces using modern JavaScript frameworks like React.js or Vue.js.
- Integrate third-party APIs and build RESTful APIs for internal and external consumption.
- Collaborate with cross-functional teams to define, design, and ship new features.
- Implement automated testing, CI/CD pipelines, and monitor system performance.
- Write clean, maintainable, and well-documented code.
- Stay up-to-date with emerging technologies and propose innovative solutions.

Skills and Qualifications
- 2+ years of experience in software development, working on both frontend and backend technologies.
- Proficiency in JavaScript, TypeScript, HTML, and CSS.
- Experience with React.js, Angular, or Vue.js for frontend development.
- Hands-on experience with backend frameworks like Express.js, Django, or Flask.
- Familiarity with databases like PostgreSQL, MySQL, or MongoDB.
- Strong understanding of version control systems (e.g., Git, GitHub, GitLab).
- Knowledge of cloud platforms such as AWS, Azure, or Google Cloud is a plus.
- Experience with containerization tools like Docker and orchestration tools like Kubernetes is a bonus.
- Excellent problem-solving and communication skills.
- Ability to work in an Agile/Scrum environment.`
  );
  const [files, setFiles] = useState<FileList | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!files) return;

    const formData = new FormData();
    formData.append("job_description", jobDescription);
    Array.from(files).forEach((file) => formData.append("resume_files", file));

    try {
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      onResults(result);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="w-[1000px] mx-auto p-6 bg-white rounded-lg shadow">
      <h1 className="text-2xl font-bold text-center mb-6">Resume Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label
            htmlFor="job_description"
            className="block text-gray-700 font-bold"
          >
            Job Description:
          </label>
          <textarea
            id="job_description"
            className="w-full mt-2 p-3 border rounded-lg h-[480px]"
            placeholder="Enter the job description here..."
            rows={6}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label
            htmlFor="resume_files"
            className="block text-gray-700 font-bold"
          >
            Upload Resumes (PDF):
          </label>
          <input
            id="resume_files"
            type="file"
            className="mt-2 block w-full text-sm text-gray-500"
            multiple
            accept=".pdf"
            onChange={(e) => setFiles(e.target.files)}
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-primary text-white py-2 px-4 rounded-lg hover:bg-secondary transition"
        >
          Analyze Resumes
        </button>
      </form>
    </div>
  );
};

export default FormComponent;
