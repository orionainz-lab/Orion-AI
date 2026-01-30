# ADR-014: AG Grid Community vs Enterprise

**Status**: ACCEPTED  
**Date**: 2026-01-30  
**Phase**: Phase 4 - Frontend  
**Deciders**: System Architect, Senior Frontend Engineer

---

## Context

The Matrix Grid requires a high-performance data grid capable of displaying 10,000+ proposals with sorting, filtering, and real-time updates. AG Grid offers two editions: Community (free, open-source) and Enterprise (paid, $999/developer/year).

---

## Decision

Start with **AG Grid Community Edition**. Upgrade to **Enterprise Edition** only if specific features are required that block MVP launch.

---

## Rationale

### Community Edition Features (Sufficient for MVP)

✅ **Virtual Scrolling**: DOM recycling for 100K+ rows  
✅ **Column Management**: Sorting, filtering, resizing, reordering  
✅ **Cell Rendering**: Custom components (StatusBadge, ActionButtons)  
✅ **Row Selection**: Single and multi-select  
✅ **CSV Export**: Basic export functionality  
✅ **Themes**: Customizable styling  
✅ **Performance**: Same rendering engine as Enterprise

**Cost**: $0 (MIT license)

### Enterprise Edition Features (Nice-to-Have)

🔒 **Row Grouping**: Group by status, user, date  
🔒 **Pivoting**: Cross-tabulation of data  
🔒 **Excel Export**: Full Excel formatting  
🔒 **Master-Detail**: Expandable row details  
🔒 **Aggregation**: Sum, count, avg across groups  
🔒 **Range Selection**: Excel-like cell selection

**Cost**: $999/developer/year

### Cost-Benefit Analysis

**Scenario 1: Community Edition**
- Cost: $0
- Features: Sufficient for core requirements (display, sort, filter, approve)
- Risk: May need upgrade later (code unchanged, license swap)

**Scenario 2: Enterprise Edition (Immediate)**
- Cost: $999/year
- Features: All features available
- Risk: Paying for unused features

**Decision**: Start with Community, upgrade if needed. **Estimated savings: $999** (if Community sufficient).

---

## Implementation Strategy

### Phase 4.1-4.2 (MVP)

Use **Community Edition**:
```bash
npm install ag-grid-community ag-grid-react
```

Implement core features:
- Matrix grid display
- Column definitions (status, workflow, created_at, actions)
- Custom cell renderers (StatusBadge, ActionButtons)
- CSV export
- Real-time row updates

### Evaluation Point (End of Phase 4.2)

**Assess if Enterprise needed**:
- ❓ Users request row grouping (group by status)?
- ❓ Excel export with formatting required?
- ❓ Master-detail for proposal breakdown needed?

**If YES to 2+**: Upgrade to Enterprise  
**If NO**: Continue with Community

### Upgrade Process (If Needed)

1. Purchase license ($999/developer)
2. Replace imports:
   ```typescript
   // Before
   import { AgGridReact } from 'ag-grid-react';
   import 'ag-grid-community/styles/ag-grid.css';
   
   // After
   import { AgGridReact } from 'ag-grid-react';
   import 'ag-grid-enterprise'; // Adds enterprise features
   import 'ag-grid-community/styles/ag-grid.css';
   ```
3. Add license key:
   ```typescript
   import { LicenseManager } from 'ag-grid-enterprise';
   LicenseManager.setLicenseKey('YOUR_LICENSE_KEY');
   ```
4. Enable enterprise features (row grouping, etc.)

**Migration Effort**: <1 hour (no code changes, just import swap)

---

## Consequences

### Positive

✅ **Cost Savings**: $0 vs $999/year (if Community sufficient)  
✅ **No Lock-in**: Can upgrade anytime without code rewrite  
✅ **Same Performance**: Virtual scrolling works identically  
✅ **Risk-Free**: Trial Enterprise features before purchasing

### Negative

⚠️ **Feature Limitations**: No row grouping, Excel export, pivoting  
⚠️ **Upgrade Friction**: Need to purchase later if required  
⚠️ **Learning Curve**: May need to learn Enterprise features later

### Mitigation

- Document Enterprise upgrade path in README
- Monitor user feedback for missing features
- Keep license purchase process simple (credit card, instant)

---

## Alternatives Considered

### Alternative 1: TanStack Table (React Table v8)

**Pros**:
- Free, open-source
- Headless (full styling control)
- Smaller bundle (~14KB)
- Active development

**Cons**:
- No built-in virtual scrolling (need separate library)
- More boilerplate for column definitions
- Less performant for 10K+ rows
- No built-in export

**Rejected Because**: Performance and features inferior to AG Grid Community.

### Alternative 2: Material-UI Data Grid

**Pros**:
- Free tier available
- Good UX out-of-box
- Material Design styling

**Cons**:
- Pro version required for >100 rows (€420/year)
- Performance degrades >1000 rows
- Heavy bundle size
- Styling less customizable

**Rejected Because**: Performance ceiling too low (needs Pro for >100 rows).

### Alternative 3: Handsontable

**Pros**:
- Excel-like experience
- Good for data entry

**Cons**:
- Commercial license required ($990/year)
- Less modern API
- Smaller community

**Rejected Because**: Similar cost to AG Grid Enterprise, but worse ecosystem.

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| **Render 10K rows** | Smooth scrolling | ⏳ (Community) |
| **Real-time updates** | <100ms per row | ⏳ (Community) |
| **CSV export** | Working | ⏳ (Community) |
| **Column sorting** | All columns | ⏳ (Community) |
| **Custom renderers** | StatusBadge, Actions | ⏳ (Community) |

If all criteria met with Community → **Stay with Community**  
If missing critical features → **Upgrade to Enterprise**

---

## References

- [AG Grid Community vs Enterprise Comparison](https://www.ag-grid.com/javascript-data-grid/licensing/)
- [AG Grid Pricing](https://www.ag-grid.com/license-pricing/)
- [AG Grid React Integration](https://www.ag-grid.com/react-data-grid/)

---

**Status**: ACCEPTED (Community Edition, upgrade path defined)  
**Last Reviewed**: 2026-01-30  
**Next Review**: End of Phase 4.2 (evaluate upgrade need)
