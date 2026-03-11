import type { Table } from '../data/stages';

interface ComparisonTableProps {
  table: Table;
}

export function ComparisonTable({ table }: ComparisonTableProps) {
  return (
    <div className="mt-6 mb-4">
      <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        {table.title}
      </h4>
      <div className="overflow-x-auto">
        <table className="framework-table">
          <thead>
            <tr>
              {table.headers.map((header) => (
                <th key={header}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.rows.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {row.map((cell, cellIdx) => (
                  <td key={cellIdx}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
