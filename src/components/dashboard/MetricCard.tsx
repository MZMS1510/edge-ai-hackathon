import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, value }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-sm text-gray-600 mb-2">{title}</h3>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
};
