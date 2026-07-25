import { getAgentForProperty } from '../utils/propertyUtils'

export default function AgentCard({ propertyId }) {
  const agent = getAgentForProperty(propertyId)

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6">
      <h3 className="text-xl font-bold mb-4">Contact Agent</h3>

      <div className="flex items-start gap-4 mb-5">
        <div className="h-14 w-14 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xl font-bold">
          {agent.name.charAt(0)}
        </div>
        <div>
          <p className="font-semibold text-lg">{agent.name}</p>
          <p className="text-sm text-slate-500 mt-1">{agent.phone}</p>
          <p className="text-sm text-slate-500">{agent.email}</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <a
          href={`tel:${agent.phone.replace(/\s/g, '')}`}
          className="inline-flex items-center gap-2 bg-primary-600 text-white px-5 py-2.5 rounded-lg font-medium hover:bg-primary-700 transition-colors duration-200"
        >
          📞 Call
        </a>
        <a
          href={`mailto:${agent.email}`}
          className="inline-flex items-center gap-2 border border-slate-300 px-5 py-2.5 rounded-lg font-medium text-slate-700 hover:bg-slate-50 transition-colors duration-200"
        >
          ✉ Email
        </a>
      </div>
    </div>
  )
}
