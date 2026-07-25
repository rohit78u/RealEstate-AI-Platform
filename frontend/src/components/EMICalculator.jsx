import { useEffect, useState } from 'react'
import { formatPrice } from '../services/api'
import { calculateEMI } from '../utils/propertyUtils'

export default function EMICalculator({ defaultLoanAmount = 0 }) {
  const [loanAmount, setLoanAmount] = useState(defaultLoanAmount || '')
  const [interestRate, setInterestRate] = useState(8.5)
  const [tenure, setTenure] = useState(20)

  useEffect(() => {
    if (defaultLoanAmount) {
      setLoanAmount(Math.round(defaultLoanAmount * 0.8))
    }
  }, [defaultLoanAmount])

  const { emi, totalInterest, totalPayment } = calculateEMI(
    loanAmount,
    interestRate,
    tenure
  )

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-xl font-bold mb-4">EMI Calculator</h3>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm text-slate-600 mb-1">Loan Amount (₹)</label>
          <input
            type="number"
            value={loanAmount}
            onChange={(e) => setLoanAmount(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Interest Rate (%)</label>
          <input
            type="number"
            step="0.1"
            value={interestRate}
            onChange={(e) => setInterestRate(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-600 mb-1">Loan Tenure (Years)</label>
          <input
            type="number"
            value={tenure}
            onChange={(e) => setTenure(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-primary-50 rounded-lg p-4">
          <p className="text-xs text-slate-500">Monthly EMI</p>
          <p className="text-xl font-bold text-primary-700">{formatPrice(emi)}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-4">
          <p className="text-xs text-slate-500">Total Interest</p>
          <p className="text-xl font-bold">{formatPrice(totalInterest)}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-4">
          <p className="text-xs text-slate-500">Total Payment</p>
          <p className="text-xl font-bold">{formatPrice(totalPayment)}</p>
        </div>
      </div>
    </div>
  )
}
