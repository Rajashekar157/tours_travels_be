from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.driver_route import router as driver_router
from routes.vehicle_route import router as vehicle_router
from routes.auth_route import router as auth_router
from routes.supplier_route import router as supplier_router
from routes.VehicleAssignments_route import router as vehicle_assignment_router
from routes.staff_route import router as staff_router
from routes.dashboard_route import router as dashboard_router

# from routes.assignment_route import router as assignment_router
# from routes.search_controller import router as search_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
         "http://147.93.103.145",
        "https://tours-travels-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(staff_router)
app.include_router(dashboard_router)
app.include_router(driver_router)
app.include_router(vehicle_router)
app.include_router(supplier_router)
app.include_router(vehicle_assignment_router)

# app.include_router(assignment_router)
# app.include_router(search_router)



