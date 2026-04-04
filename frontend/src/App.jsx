import React, { useState } from 'react'

const BASE_URL = 'http://localhost:8080'

const ZONES = [
  { id: 1, name: "Velachery", riskType: "FLOOD_PRONE" },
  { id: 2, name: "Pallikaranai", riskType: "FLOOD_PRONE" },
  { id: 3, name: "T Nagar", riskType: "HEAT_HEAVY" },
  { id: 4, name: "Guindy", riskType: "HEAT_HEAVY" },
  { id: 5, name: "Adyar", riskType: "MIXED" },
]

const RISK_SUMMARIES = {
  FLOOD_PRONE: [
    "Flood-prone zone — lower rainfall threshold applied",
    "Historically higher rain-triggered claim frequency",
  ],
  HEAT_HEAVY: [
    "Heat-sensitive zone — temperature threshold lowered to 38 C",
    "Peak-hour heat exposure increases income loss probability",
  ],
  MIXED: [
    "Mixed disruption profile — multiple trigger types monitored",
    "Moderate baseline risk across weather categories",
  ],
}

function App() {
  const [user, setUser] = useState({ name: '', zoneId: 1, dailyHours: 8, peakHours: true })
  const [session, setSession] = useState({
    userId: null, policyId: null, premium: null, maxCap: null,
    riskLevel: null, zoneName: null, zoneRiskType: null,
  })
  const [claims, setClaims] = useState([])
  const [simLoading, setSimLoading] = useState(false)
  const [simResults, setSimResults] = useState([])  // history of checks
  const [toast, setToast] = useState(null)

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const delay = (ms) => new Promise(r => setTimeout(r, ms))

  const handleRegister = async () => {
    try {
      const res = await fetch(`${BASE_URL}/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: user.name || "Demo Partner",
          zone_id: user.zoneId,
          daily_working_hours: user.dailyHours,
          works_peak_hours: user.peakHours
        })
      })
      const data = await res.json()
      setSession(s => ({ ...s, userId: data.id }))
      showToast('Delivery partner registered successfully')
    } catch (e) {
      showToast(`Registration failed: ${e.message}`, 'error')
    }
  }

  const handleCreatePolicy = async () => {
    if (!session.userId) return showToast('Register a user first', 'error')
    try {
      const res = await fetch(`${BASE_URL}/policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: session.userId })
      })
      const data = await res.json()
      setSession(s => ({
        ...s,
        policyId: data.id,
        premium: data.premium,
        maxCap: data.max_payout_cap,
        riskLevel: data.risk_level,
        zoneName: data.zone_name,
        zoneRiskType: data.zone_risk_type,
      }))
      showToast(`Policy issued at ${data.premium}/week`)
    } catch (e) {
      showToast(`Policy creation failed: ${e.message}`, 'error')
    }
  }

  const handleCheck = async (type) => {
    const zoneName = ZONES.find(z => z.id === user.zoneId)?.name || 'Velachery'
    setSimLoading(true)

    await delay(800)

    try {
      const res = await fetch(`${BASE_URL}/simulate-event?zone=${zoneName}&type=${type}`)
      const data = await res.json()

      const entry = {
        id: Date.now(),
        type,
        status: data.status,
        result: data.result,
        conditions: data.conditions || {},
        zone: data.zone,
      }
      setSimResults(prev => [entry, ...prev].slice(0, 8))

      if (data.status === 'triggered') {
        showToast('Disruption confirmed — claim generated')
        fetchClaims()
      } else {
        showToast('No disruption detected', 'info')
      }
    } catch (e) {
      showToast(`Check failed: ${e.message}`, 'error')
    } finally {
      setSimLoading(false)
    }
  }

  const fetchClaims = async () => {
    if (!session.userId) return
    try {
      const res = await fetch(`${BASE_URL}/claims/${session.userId}`)
      const data = await res.json()
      setClaims(data.claims || [])
    } catch (e) {
      showToast('Failed to fetch claims', 'error')
    }
  }

  function parseExplanation(reason) {
    if (!reason) return []
    return reason.split(' | ').map(part => {
      const [label, ...rest] = part.split(': ')
      return { label: label.trim(), value: rest.join(': ').trim() }
    })
  }

  function getRiskBadge(level) {
    if (level === 'High') return 'bg-red-50 text-red-700 border-red-200'
    if (level === 'Medium') return 'bg-amber-50 text-amber-700 border-amber-200'
    return 'bg-green-50 text-green-700 border-green-200'
  }

  function formatConditions(c) {
    const parts = []
    if (c.rainfall_mm !== undefined) parts.push(`Rainfall: ${c.rainfall_mm}mm`)
    if (c.waterlogging !== undefined) parts.push(`Waterlogging: ${c.waterlogging ? 'yes' : 'no'}`)
    if (c.temperature_c !== undefined) parts.push(`Temp: ${c.temperature_c} C`)
    if (c.orders_per_hour !== undefined) parts.push(`Orders/hr: ${c.orders_per_hour}/150`)
    return parts.join('  ·  ')
  }

  const summaryLines = session.zoneRiskType ? RISK_SUMMARIES[session.zoneRiskType] || [] : []

  const stepDone = (i) => {
    if (i === 0) return !!session.userId
    if (i === 1) return !!session.policyId
    if (i === 2) return simResults.length > 0
    if (i === 3) return claims.length > 0
    return false
  }

  return (
    <div className="min-h-screen bg-gray-50">

      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium
          ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-gray-900 text-white'}`}>
          {toast.msg}
        </div>
      )}

      {/* Top Bar */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Parametric Insurance Engine</h1>
            <p className="text-xs text-gray-500">Guidewire DEVTrails 2026 — Phase 2 Prototype</p>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-gray-400">
            {['Register', 'Policy', 'Monitor', 'Claims'].map((step, i) => (
              <React.Fragment key={step}>
                <span className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-semibold
                  ${stepDone(i) ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                  {stepDone(i) ? '\u2713' : i + 1}
                </span>
                <span className={`${stepDone(i) ? 'text-gray-700' : 'text-gray-400'} hidden sm:inline`}>{step}</span>
                {i < 3 && <span className="text-gray-300 mx-0.5">/</span>}
              </React.Fragment>
            ))}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

          {/* Section 1: Registration */}
          <section className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="mb-5">
              <span className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Step 1</span>
              <h2 className="text-base font-semibold text-gray-900 mt-0.5">Delivery Partner Registration</h2>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Partner Name</label>
                <input type="text"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g. Ramesh"
                  value={user.name}
                  onChange={e => setUser({ ...user, name: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Operating Zone</label>
                <select
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={user.zoneId}
                  onChange={e => setUser({ ...user, zoneId: parseInt(e.target.value) })}>
                  {ZONES.map(z => <option key={z.id} value={z.id}>{z.name}</option>)}
                </select>
              </div>
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    checked={user.peakHours}
                    onChange={e => setUser({ ...user, peakHours: e.target.checked })} />
                  Works peak hours
                </label>
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-500">Hours/day</label>
                  <input type="number" min="1" max="16"
                    className="w-16 border border-gray-300 rounded-md px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={user.dailyHours}
                    onChange={e => setUser({ ...user, dailyHours: parseInt(e.target.value) || 8 })} />
                </div>
              </div>
              <button onClick={handleRegister}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2.5 rounded-md transition-colors">
                Register Partner
              </button>
            </div>
            {session.userId && (
              <div className="mt-4 bg-gray-50 border border-gray-200 rounded-md p-3">
                <div className="text-xs font-medium text-green-700 mb-1">Registered</div>
                <div className="text-xs text-gray-500 font-mono break-all">{session.userId}</div>
              </div>
            )}
          </section>

          {/* Section 2: Risk & Policy */}
          <section className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="mb-5">
              <span className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Step 2</span>
              <h2 className="text-base font-semibold text-gray-900 mt-0.5">Risk Scoring & Policy</h2>
            </div>
            {session.userId ? (
              <div className="space-y-4">
                <button onClick={handleCreatePolicy}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2.5 rounded-md transition-colors">
                  Run Risk Engine
                </button>
                {session.policyId && (
                  <>
                    <div className="border border-gray-200 rounded-md p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="text-xs text-gray-500 font-medium uppercase tracking-wider">Weekly Premium</div>
                          <div className="text-3xl font-bold text-gray-900 mt-1">{'\u20B9'}{session.premium}</div>
                        </div>
                        <div className="text-right">
                          <span className={`inline-block text-xs font-semibold px-2.5 py-1 rounded-full border ${getRiskBadge(session.riskLevel)}`}>
                            {session.riskLevel} Risk
                          </span>
                          <div className="text-xs text-gray-500 mt-1.5">{session.zoneName}</div>
                        </div>
                      </div>
                      <div className="border-t border-gray-100 pt-3 flex justify-between text-sm">
                        <span className="text-gray-500">Weekly payout cap</span>
                        <span className="font-semibold text-gray-900">{'\u20B9'}{session.maxCap}</span>
                      </div>
                    </div>
                    <div className="border border-gray-200 rounded-md p-4">
                      <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3">Risk Summary</h3>
                      <ul className="space-y-2">
                        {summaryLines.map((line, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                            <span className="w-1 h-1 rounded-full bg-gray-400 mt-2 shrink-0"></span>
                            {line}
                          </li>
                        ))}
                        {user.peakHours && (
                          <li className="flex items-start gap-2 text-sm text-amber-700">
                            <span className="w-1 h-1 rounded-full bg-amber-500 mt-2 shrink-0"></span>
                            Peak-hour dependency increases premium exposure
                          </li>
                        )}
                      </ul>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-sm text-gray-400 py-12 text-center">Complete Step 1 to continue</div>
            )}
          </section>

          {/* Section 3: Weather Monitor */}
          <section className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="mb-5">
              <span className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Step 3</span>
              <h2 className="text-base font-semibold text-gray-900 mt-0.5">Weather Condition Monitor</h2>
            </div>
            <div className="space-y-3">
              <button disabled={!session.policyId || simLoading} onClick={() => handleCheck('rain')}
                className="w-full text-left border border-gray-200 rounded-md p-3.5 hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
                <div className="text-sm font-semibold text-gray-900">Check Rain Conditions</div>
                <div className="text-xs text-gray-500 mt-0.5">Query rainfall and waterlogging status</div>
              </button>
              <button disabled={!session.policyId || simLoading} onClick={() => handleCheck('heat')}
                className="w-full text-left border border-gray-200 rounded-md p-3.5 hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed">
                <div className="text-sm font-semibold text-gray-900">Check Heat Conditions</div>
                <div className="text-xs text-gray-500 mt-0.5">Query temperature and activity levels</div>
              </button>
            </div>

            {/* Loading state */}
            {simLoading && (
              <div className="mt-4 border border-gray-200 rounded-md p-3 bg-gray-50">
                <div className="text-sm text-gray-600">Checking weather API...</div>
              </div>
            )}

            {/* Results history */}
            {simResults.length > 0 && !simLoading && (
              <div className="mt-4 space-y-2">
                <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Recent Checks</div>
                {simResults.map(r => (
                  <div key={r.id} className={`border rounded-md p-3 ${r.status === 'triggered' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white'}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-xs font-semibold ${r.status === 'triggered' ? 'text-green-700' : 'text-gray-500'}`}>
                        {r.status === 'triggered' ? 'DISRUPTION TRIGGERED' : 'NO DISRUPTION'}
                      </span>
                      <span className="text-[10px] text-gray-400 uppercase">{r.type} / {r.zone}</span>
                    </div>
                    <div className="text-xs text-gray-600">{formatConditions(r.conditions)}</div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Section 4: Claims */}
          <section className="bg-white border border-gray-200 rounded-lg p-6 flex flex-col">
            <div className="flex items-center justify-between mb-5">
              <div>
                <span className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider">Step 4</span>
                <h2 className="text-base font-semibold text-gray-900 mt-0.5">Claims & Payouts</h2>
              </div>
              <button onClick={fetchClaims}
                className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors">
                Refresh
              </button>
            </div>
            <div className="flex-1 space-y-3 overflow-y-auto max-h-[420px]">
              {claims.length === 0 ? (
                <div className="text-sm text-gray-400 text-center py-16">No claims yet</div>
              ) : (
                claims.map(c => {
                  const parts = parseExplanation(c.trigger_reason)
                  const isFraud = c.fraud_flag === 1
                  return (
                    <div key={c.id} className={`border rounded-md overflow-hidden ${isFraud ? 'border-red-200' : 'border-gray-200'}`}>
                      <div className={`flex items-center justify-between px-4 py-3 ${isFraud ? 'bg-red-50' : 'bg-gray-50'} border-b border-gray-200`}>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-gray-700">{c.trigger_type}</span>
                          {isFraud && (
                            <span className="text-[10px] font-semibold text-red-700 bg-red-100 px-1.5 py-0.5 rounded">Flagged</span>
                          )}
                        </div>
                        <div className={`text-xl font-bold ${isFraud ? 'text-red-600' : 'text-green-700'}`}>
                          {'\u20B9'}{c.payout_amount}
                        </div>
                      </div>
                      <div className="px-4 py-3 space-y-1.5">
                        {parts.map((p, i) => (
                          <div key={i} className="flex gap-3 text-xs">
                            <span className="text-gray-400 font-medium w-28 shrink-0">{p.label}</span>
                            <span className={`text-gray-700 ${p.label === 'Cap Notice' ? 'text-amber-700 font-medium' : ''}`}>
                              {p.value}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </section>

        </div>
      </main>
    </div>
  )
}

export default App
