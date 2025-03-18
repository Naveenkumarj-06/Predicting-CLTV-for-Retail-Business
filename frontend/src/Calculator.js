import { useState } from 'react';
import { Link } from 'react-router-dom';



const CLVCalculator = () => {
  const [acquisitionCost, setAcquisitionCost] = useState(2);
  const [revenuePerUser, setRevenuePerUser] = useState(97);
  const [retentionRate, setRetentionRate] = useState(3);
  const [numberOfCustomers, setNumberOfCustomers] = useState(3);
  const [clv, setClv] = useState(280);

  const calculateCLV = () => {
    if (acquisitionCost === 0) {
      setClv(0);
      return;
    }
    const calculatedCLV = (revenuePerUser * retentionRate * numberOfCustomers) / acquisitionCost;
    setClv(Math.round(calculatedCLV));
  };

  return (
    <div className="max-w-3xl mx-auto p-8 bg-gradient-to-br from-blue-50 to-white rounded-2xl shadow-lg">
      <header className="text-center mb-8">
        <h1 className="text-4xl font-extrabold text-blue-700 mb-2">CLV Calculator</h1>
        <p className="text-gray-600 text-lg">Estimate your Customer Lifetime Value</p>
      </header>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-gray-700 font-semibold">Acquisition Cost</label>
          <input
            type="number"
            value={acquisitionCost}
            onChange={(e) => setAcquisitionCost(parseFloat(e.target.value))}
            className="border p-3 w-full rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold">Revenue Per User</label>
          <input
            type="number"
            value={revenuePerUser}
            onChange={(e) => setRevenuePerUser(parseFloat(e.target.value))}
            className="border p-3 w-full rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold">Retention Rate</label>
          <input
            type="number"
            value={retentionRate}
            onChange={(e) => setRetentionRate(parseFloat(e.target.value))}
            className="border p-3 w-full rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-semibold">Number of Customers</label>
          <input
            type="number"
            value={numberOfCustomers}
            onChange={(e) => setNumberOfCustomers(parseFloat(e.target.value))}
            className="border p-3 w-full rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="clv-result-box">
  <p>Customer Lifetime Value</p>
  <div className="clv-value">${clv}</div>
</div>

<button
  onClick={calculateCLV}
  className="w-full bg-blue-600 text-white py-3 rounded-xl text-lg font-semibold hover:bg-blue-700 transition duration-200"
>
  CALCULATE
</button>


      <div className="text-center mt-6">
        <Link to="/" className="text-blue-600 hover:underline font-semibold">
          ← Back to Home
        </Link>
      </div>
    </div>
  );
};

export default CLVCalculator;
