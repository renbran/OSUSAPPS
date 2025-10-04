# ⚡ Odoo 17 Performance-Focused Code Review Template

## Performance Review Information

- **Module Name**: `[module_name]`
- **Performance Reviewer**: `[reviewer_name]`
- **Review Date**: `[date]`
- **Review Type**: Performance Assessment
- **Performance Category**: `[DATABASE/FRONTEND/BACKEND/FULL_STACK]`

## 🚀 Performance Assessment Checklist

### 🗄️ Database Performance

- [ ] **Query Optimization**
  - [ ] No N+1 query patterns
  - [ ] Efficient search domains used
  - [ ] Proper use of `limit` in searches
  - [ ] Bulk operations instead of loops
  - [ ] Appropriate use of `exists()` vs `search()`

- [ ] **ORM Efficiency**
  - [ ] Minimal record.browse() calls
  - [ ] Proper use of recordsets
  - [ ] Field access optimized
  - [ ] Related fields used appropriately
  - [ ] Computed fields efficiently implemented

- [ ] **Database Schema**
  - [ ] Appropriate field types chosen
  - [ ] Database indexes considered
  - [ ] Foreign key relationships optimized
  - [ ] No unnecessary field computations

### 🧮 Computed Fields & Dependencies

- [ ] **Compute Method Efficiency**
  - [ ] Proper `@api.depends` declarations
  - [ ] Minimal computations per record
  - [ ] Batch operations in compute methods
  - [ ] No recursive computations
  - [ ] Store=True used appropriately

- [ ] **Field Dependencies**
  - [ ] Dependencies accurately declared
  - [ ] No over-computation of fields
  - [ ] Cascade dependencies minimized
  - [ ] Related field performance considered

### 📊 Search & Filtering Performance

- [ ] **Search Domains**
  - [ ] Indexed fields used in search
  - [ ] Domain optimization applied
  - [ ] No unnecessary domain complexity
  - [ ] Proper use of search_count()

- [ ] **Filter Implementation**
  - [ ] Custom filters optimized
  - [ ] Default filters efficient
  - [ ] Search view performance tested
  - [ ] Faceted search optimized

### 🔄 Workflow & State Management

- [ ] **State Transitions**
  - [ ] Minimal state computation
  - [ ] Efficient workflow methods
  - [ ] No unnecessary state checks
  - [ ] Batch state updates

- [ ] **Business Logic**
  - [ ] Complex logic optimized
  - [ ] Caching implemented where beneficial
  - [ ] Minimal external API calls
  - [ ] Efficient data validation

### 📱 Frontend Performance

- [ ] **JavaScript Optimization**
  - [ ] Minimal DOM manipulations
  - [ ] Efficient event handling
  - [ ] Proper memory management
  - [ ] No memory leaks

- [ ] **OWL Components**
  - [ ] Component rendering optimized
  - [ ] Proper lifecycle management
  - [ ] Minimal re-renders
  - [ ] Efficient state management

- [ ] **Asset Loading**
  - [ ] CSS/JS properly minified
  - [ ] Assets bundled efficiently
  - [ ] Lazy loading implemented
  - [ ] CDN usage optimized

### 🎨 View Performance

- [ ] **QWeb Templates**
  - [ ] Minimal template complexity
  - [ ] Efficient loops and conditions
  - [ ] No unnecessary field access
  - [ ] Proper caching headers set

- [ ] **Form Views**
  - [ ] Field loading optimized
  - [ ] Related fields minimized
  - [ ] Widget performance tested
  - [ ] Tab loading efficient

- [ ] **List Views**
  - [ ] Column count optimized
  - [ ] Pagination properly implemented
  - [ ] Sorting performance tested
  - [ ] Export functionality efficient

### 🌐 API & Controllers

- [ ] **HTTP Controllers**
  - [ ] Response time optimized
  - [ ] Proper caching implemented
  - [ ] Minimal database queries
  - [ ] Efficient JSON serialization

- [ ] **RPC Calls**
  - [ ] Minimal client-server roundtrips
  - [ ] Batch operations implemented
  - [ ] Proper error handling
  - [ ] Response size optimized

### 📈 Reporting Performance

- [ ] **Report Generation**
  - [ ] Query optimization for reports
  - [ ] Minimal data processing
  - [ ] Efficient PDF generation
  - [ ] Excel export optimized

- [ ] **Dashboard Performance**
  - [ ] Chart data optimized
  - [ ] Real-time updates efficient
  - [ ] Caching implemented
  - [ ] Mobile performance tested

## 📊 Performance Issues Found

### Critical Performance Issues
```plaintext
[Issues causing significant performance degradation]
- [CRITICAL] Issue description
  Location: file:line
  Impact: Performance impact description
  Measurement: Before/after metrics
  Remediation: Required optimization
```

### High Performance Issues
```plaintext
[Issues causing noticeable performance impact]
- [HIGH] Issue description
  Location: file:line
  Impact: Performance impact description
  Measurement: Performance metrics
  Remediation: Recommended optimization
```

### Medium Performance Issues
```plaintext
[Issues with moderate performance impact]
- [MEDIUM] Issue description
  Location: file:line
  Impact: Performance impact description
  Measurement: Performance metrics
  Remediation: Suggested optimization
```

### Low Performance Issues
```plaintext
[Minor performance improvements]
- [LOW] Issue description
  Location: file:line
  Impact: Performance impact description
  Measurement: Performance metrics
  Remediation: Optional optimization
```

## ⚡ Performance Recommendations

### Database Optimizations
```plaintext
1. Optimization 1
   - Implementation details
   - Expected improvement
2. Optimization 2
   - Implementation details
   - Expected improvement
```

### Code Optimizations
```plaintext
1. Code change 1
   - Specific modification needed
   - Performance benefit
2. Code change 2
   - Specific modification needed
   - Performance benefit
```

### Architecture Improvements
```plaintext
1. Architectural change 1
   - Design modification
   - Scalability benefit
2. Architectural change 2
   - Design modification
   - Scalability benefit
```

## 📈 Performance Metrics

### Load Testing Results

| Scenario | Users | Response Time | Throughput | Resource Usage |
|----------|-------|---------------|------------|----------------|
| Login Flow | 100 | `[ms]` | `[req/s]` | `[CPU/Memory %]` |
| List View | 50 | `[ms]` | `[req/s]` | `[CPU/Memory %]` |
| Form View | 50 | `[ms]` | `[req/s]` | `[CPU/Memory %]` |
| Report Generation | 10 | `[ms]` | `[req/s]` | `[CPU/Memory %]` |

### Database Performance

| Query Type | Count | Avg Duration | Max Duration | Optimization |
|------------|-------|--------------|--------------|--------------|
| SELECT | `[count]` | `[ms]` | `[ms]` | `[status]` |
| INSERT | `[count]` | `[ms]` | `[ms]` | `[status]` |
| UPDATE | `[count]` | `[ms]` | `[ms]` | `[status]` |
| DELETE | `[count]` | `[ms]` | `[ms]` | `[status]` |

### Frontend Performance

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| First Paint | `[ms]` | < 1000ms | ✅ Pass / ❌ Fail |
| Time to Interactive | `[ms]` | < 3000ms | ✅ Pass / ❌ Fail |
| Bundle Size | `[KB]` | < 500KB | ✅ Pass / ❌ Fail |
| Memory Usage | `[MB]` | < 100MB | ✅ Pass / ❌ Fail |

## 🎯 Performance Targets

### Response Time Targets
- **Form Views**: < 500ms
- **List Views**: < 300ms  
- **Search Operations**: < 200ms
- **Report Generation**: < 2000ms
- **API Endpoints**: < 100ms

### Scalability Targets
- **Concurrent Users**: > 100
- **Database Records**: > 100,000
- **Memory Usage**: < 2GB
- **CPU Usage**: < 80%

### Browser Performance
- **Page Load Time**: < 3 seconds
- **JavaScript Execution**: < 100ms
- **Memory Leaks**: None detected
- **Mobile Performance**: 60 FPS

## ⚖️ Performance vs Feature Trade-offs

### Identified Trade-offs
```plaintext
1. Feature vs Performance consideration
   - Feature benefit
   - Performance cost
   - Recommendation

2. Feature vs Performance consideration
   - Feature benefit
   - Performance cost
   - Recommendation
```

### Optimization Priorities
1. **High Impact, Low Effort**: `[optimizations]`
2. **High Impact, High Effort**: `[optimizations]`
3. **Low Impact, Low Effort**: `[optimizations]`
4. **Low Impact, High Effort**: `[optimizations]`

## 🔧 Performance Tooling

### Profiling Tools Used
- [ ] Odoo Performance Profiler
- [ ] PostgreSQL EXPLAIN ANALYZE
- [ ] Browser DevTools
- [ ] Memory Profiler
- [ ] Load Testing Tools

### Monitoring Recommendations
```plaintext
1. Monitoring tool 1
   - Setup instructions
   - Key metrics to track

2. Monitoring tool 2
   - Setup instructions
   - Key metrics to track
```

## ✅ Performance Approval

### Performance Assessment
- [ ] **Meets Performance Requirements** - All targets achieved
- [ ] **Acceptable with Monitoring** - Close to targets, monitoring needed
- [ ] **Requires Optimization** - Performance targets not met
- [ ] **Performance Rejected** - Significant performance issues

### Performance Score
```plaintext
Database Performance: [score]/10
Frontend Performance: [score]/10
Scalability: [score]/10
Resource Efficiency: [score]/10
Overall Performance Score: [score]/10
```

### Conditions for Approval
```plaintext
1. Condition 1
2. Condition 2
```

## 🔄 Performance Follow-up

### Immediate Actions (< 24 hours)
- [ ] Fix critical performance issues
- [ ] Implement emergency optimizations
- [ ] Monitor resource usage

### Short-term Actions (< 1 week)
- [ ] Implement recommended optimizations
- [ ] Add performance monitoring
- [ ] Load test with fixes

### Long-term Actions (next iteration)
- [ ] Architecture improvements
- [ ] Advanced optimizations
- [ ] Performance monitoring dashboard

## 📝 Performance Notes
```plaintext
[Additional performance observations, bottlenecks, or recommendations]
```

## ⚡ Performance Reviewer Sign-off

- **Reviewer Name**: `[name]`
- **Date**: `[date]`
- **Performance Score**: `[score]/10`
- **Recommendation**: `[APPROVE/CONDITIONAL/OPTIMIZE]`
- **Next Review Date**: `[date]`

---

**Performance Review Template Version**: 1.0
**OSUSAPPS Performance Standards**: Odoo 17 Enterprise
**Last Updated**: `[current_date]`