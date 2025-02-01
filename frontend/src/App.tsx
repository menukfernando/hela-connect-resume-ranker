import React, { useState } from 'react';
import FormComponent from './components/FormComponent';
import ResultsTable from './components/ResultsTable';
import './App.css'

const App: React.FC = () => {
  const [results, setResults] = useState<any[]>([]);

  const handleResults = (newResults: any[]) => {
    setResults(newResults);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4 flex flex-col justify-center">
      <FormComponent onResults={handleResults} />
      {results.length > 0 && <ResultsTable results={results} />}
    </div>
  );
};

export default App;
