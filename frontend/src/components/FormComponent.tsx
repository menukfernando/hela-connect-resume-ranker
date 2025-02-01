import React, { useState } from 'react';

interface FormComponentProps {
  onResults: (results: any[]) => void; // Prop to pass results to parent
}

const FormComponent: React.FC<FormComponentProps> = ({ onResults }) => {
  const [jobDescription, setJobDescription] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!files) return;

    const formData = new FormData();
    formData.append('job_description', jobDescription);
    Array.from(files).forEach((file) => formData.append('resume_files', file));

    try {
      const response = await fetch('http://127.0.0.1:5000/', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      onResults(result); // Pass results to parent component
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="w-[600px] mx-auto p-6 bg-white rounded-lg shadow">
      <h1 className="text-2xl font-bold text-center mb-6">Resume Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="job_description" className="block text-gray-700 font-bold">
            Job Description:
          </label>
          <textarea
            id="job_description"
            className="w-full mt-2 p-3 border rounded-lg"
            placeholder="Enter the job description here..."
            rows={4}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label htmlFor="resume_files" className="block text-gray-700 font-bold">
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
          className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600"
        >
          Analyze Resumes
        </button>
      </form>
    </div>
  );
};

export default FormComponent;
