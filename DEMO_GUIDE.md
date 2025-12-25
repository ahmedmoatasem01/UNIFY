# Study Plan Generator - Demo Guide

## Quick Start

### Running the Demo

1. **Navigate to the UNIFY directory:**
   ```bash
   cd "C:\Users\ALI ABOZEKRY\OneDrive\Desktop\new_sw\UNIFY"
   ```

2. **Run the demo server:**
   ```bash
   python demo_study_planner.py
   ```

3. **Access the demo:**
   - Open your browser and go to: **http://localhost:5001**
   - Or: **http://127.0.0.1:5001**

### What You'll See

The demo runs on **port 5001** (separate from the main app on port 5000) and includes:

- ✨ Beautiful landing page with feature showcase
- 📚 Study plans list view
- 📋 Detailed plan view with task management
- 🤖 AI-powered features demonstration
- 📊 Progress tracking and analytics

### Features to Explore

1. **Create a Study Plan**
   - Click "Create New Plan"
   - Fill in plan details
   - Let AI generate your personalized schedule

2. **Manage Tasks**
   - Add tasks manually
   - Enable auto-decomposition for large tasks (>4 hours)
   - Track progress with completion percentages

3. **View Recommendations**
   - AI-generated study resource suggestions
   - Categorized by type (notes, videos, practice, textbooks)

4. **Adjust Plans**
   - Automatically reschedule overdue tasks
   - Adapt to changing deadlines

### Database Setup (Optional)

For full functionality, run the SQL schema:

```sql
-- In SQL Server Management Studio or sqlcmd:
USE your_database;
GO

-- Run the schema file:
:r "C:\Users\ALI ABOZEKRY\OneDrive\Desktop\new_sw\UNIFY\database\study_plan_schema.sql"
GO
```

### Demo vs. Full App

| Feature | Demo (Port 5001) | Full App (Port 5000) |
|---------|------------------|----------------------|
| Study Plans UI | ✅ | ✅ |
| Database Integration | ⚠️ Requires setup | ✅ |
| Other Features | ❌ | ✅ |
| Authentication | Demo user | Full auth |

### Troubleshooting

**Port already in use?**
```bash
# Change port in demo_study_planner.py line 69:
app.run(debug=True, host='0.0.0.0', port=5002)  # Use different port
```

**Database errors?**
- The demo will show UI even without database
- Some features require database setup
- Check connection string in `src/core/db_singleton.py`

**Module not found?**
```bash
# Make sure you're in the UNIFY directory
cd "C:\Users\ALI ABOZEKRY\OneDrive\Desktop\new_sw\UNIFY"
python demo_study_planner.py
```

### Keyboard Shortcuts

- **Ctrl+C** - Stop the server
- **F5** - Refresh browser to see changes

### Next Steps

1. ✅ Explore the demo UI
2. ✅ Test creating study plans
3. ✅ Try task management features
4. ✅ View AI recommendations
5. 📖 Read full documentation in `docs/STUDY_PLAN_GENERATOR.md`

### Support

For issues or questions:
- Check `docs/STUDY_PLAN_GENERATOR.md` for detailed documentation
- Review the troubleshooting section above
- Inspect browser console for errors (F12)

---

**Enjoy exploring the Smart Study Plan Generator! 🎓**
