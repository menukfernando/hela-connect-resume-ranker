import React from 'react';

interface Result {
  rank: number;
  name: string;
  email: string;
  similarity: number;
}

interface ResultsTableProps {
  results: Result[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  return (
    <div className="mt-8">
      <h2 className="text-xl font-bold mb-4">Ranked Resumes</h2>
      <table className="w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 p-2">Rank</th>
            <th className="border border-gray-300 p-2">Name</th>
            <th className="border border-gray-300 p-2">Email</th>
            <th className="border border-gray-300 p-2">Similarity (%)</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result, index) => (
            <tr key={index}>
              <td className="border border-gray-300 p-2 text-center">{result.rank}</td>
              <td className="border border-gray-300 p-2">{result.name}</td>
              <td className="border border-gray-300 p-2">{result.email}</td>
              <td className="border border-gray-300 p-2 text-center">{result.similarity.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
