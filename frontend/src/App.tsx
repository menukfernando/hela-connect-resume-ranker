import React, { useState } from 'react';
import FormComponent, { IResults } from './components/FormComponent';
import ResultsTable from './components/ResultsTable';
import './App.css'

const App: React.FC = () => {
  const [results, setResults] = useState<IResults[]>([]);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const handleResults = (newResults: IResults[]) => {
    setResults(newResults);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="relative min-h-screen bg-gray-100 p-4">
      <FormComponent onResults={handleResults} />

      {isModalOpen && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-transparent backdrop-blur-sm z-50"
          onClick={handleCloseModal}
        >
          <div
            className="bg-white rounded-lg shadow-lg p-6 w-full max-w-3xl relative"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="absolute top-2 right-2 text-gray-500 hover:text-gray-700 text-2xl"
              onClick={handleCloseModal}
            >
              ✕
            </button>
            <ResultsTable results={results} />
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
