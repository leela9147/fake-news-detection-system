export default function Badge({ value }) {
  const map = {
    'LIKELY REAL': { c: 'badge-real', t: 'Likely Real' },
    'LIKELY FAKE': { c: 'badge-fake', t: 'Likely Fake' },
    'NEEDS VERIFICATION': { c: 'badge-review', t: 'Needs Verification' },
    'SUPPORTING': { c: 'badge-real', t: 'Supporting' },
    'CONTRADICTING': { c: 'badge-fake', t: 'Contradicting' },
    'INSUFFICIENT': { c: 'badge-review', t: 'Insufficient' },
    'UNAVAILABLE': { c: 'badge-review', t: 'Unavailable' },
  }
  const m = map[value] || { c: 'badge-review', t: value }
  return <span className={`badge ${m.c}`}>{m.t}</span>
}
