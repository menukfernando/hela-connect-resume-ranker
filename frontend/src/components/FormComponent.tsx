import React, { useState } from "react";
import { INITIAL_JOB_DESCRIPTION } from "../constants/constants";

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
  const [jobDescription, setJobDescription] = useState<string>(INITIAL_JOB_DESCRIPTION);
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!files) return;

    const formData = new FormData();
    formData.append("job_description", jobDescription);
    Array.from(files).forEach((file) => formData.append("resume_files", file));

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      onResults(result);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-[1000px] mx-auto p-6 bg-white rounded-lg shadow">
      <h1 className="text-2xl font-bold text-center mb-6">
        Resume Analyzer - Hela Connect Demo
      </h1>
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
            className="w-full mt-2 p-3 border rounded-lg h-[400px]"
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
            className="mt-2 w-48 p-1 rounded-md text-sm text-gray-500 bg-gray-300 cursor-pointer"
            multiple
            accept=".pdf"
            onChange={(e) => setFiles(e.target.files)}
            required
          />
        </div>
        <button
          type="submit"
          className={`w-full py-2 px-4 rounded-lg transition ${
            loading
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-primary text-white hover:bg-secondary"
          }`}
          disabled={loading}
        >
          {loading ? "Analyzing..." : "Analyze Resumes"}{" "}
        </button>
      </form>
      {loading && (
        <div className="mt-4 text-center text-gray-500">
          <p>Processing resumes... Please wait.</p>
        </div>
      )}
    </div>
  );
};

export default FormComponent;
