from app.schemas.report import Report, ReportStatus
from pathlib import Path
import json, os
from typing import List, Dict, Optional, Any

class ReportRepository: #almost the exact same as the order repository
    
    def __init__(self):
        self.data_path = Path(__file__).resolve().parents[1] / "data" / "reports.json" 
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> List[Dict[str, Any]]: #grab all data from json
        if not self.data_path.exists():
            return []
            
        with self.data_path.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_all(self, items: List[Dict[str, Any]]) -> None: #save all data to json 
        tmp = self.data_path.with_suffix(".tmp")
        
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
            
        os.replace(tmp, self.data_path)

    def get_all_reports(self) -> List[Report]:
        return [Report(**r) for r in self.load_all()] #returning as report objects instead of dicts

    def next_id(self) -> int: #for adding new report, just make next id one higher than max
        reports = self.load_all()

        if len(reports) == 0:
            return 1 
        all_ids = [report["id"] for report in reports]
        highest_id = max(all_ids)
        return highest_id + 1
    
    def save(self, report: Report) -> Report:
        # Auto-assign an ID if it's a brand new report
        if report.id == 0:
            report.id = self.next_id()
            
        reports = self.load_all()
        report_dict = report.model_dump(mode='json') #convert report object to dict for saving
        
        for i, r in enumerate(reports):
            if r["id"] == report.id:
                reports[i] = report_dict
                self.save_all(reports)
                return report # return the saved report
        
        reports.append(report_dict)
        self.save_all(reports)
        return report

    def find_by_id(self, report_id: int) -> Optional[Report]:
        reports = self.load_all()
        for r in reports:
            if r["id"] == report_id:
                return Report(**r) #return report as object
        return None
    
    def get_all_pending(self) -> List[Report]:
        # Return only the reports that have not been handled by an admin yet
        all_reports = self.get_all_reports()
        return [r for r in all_reports if r.status == ReportStatus.OPEN]
        
    def clear_all(self) -> None:
        self.save_all([])

report_db = ReportRepository()