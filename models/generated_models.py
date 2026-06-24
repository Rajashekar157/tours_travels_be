from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


t_dashboard_summary = Table(
    'dashboard_summary', Base.metadata,
    Column('total_drivers', BigInteger),
    Column('total_vehicles', BigInteger),
    Column('assigned_vehicles', BigInteger),
    Column('unassigned_vehicles', BigInteger),
    Column('active_drivers', BigInteger),
    Column('inactive_drivers', BigInteger),
    Column('outstanding_amount', Numeric)
)


class MasterFuelIssue(Base):
    __tablename__ = 'master_fuel_issue'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_fuel_issue_pkey'),
        UniqueConstraint('fuel_issue_name', name='master_fuel_issue_fuel_issue_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fuel_issue_name: Mapped[str] = mapped_column(String(50), nullable=False)

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='fuel_issue')


class MasterFuelType(Base):
    __tablename__ = 'master_fuel_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_fuel_type_pkey'),
        UniqueConstraint('fuel_type_name', name='master_fuel_type_fuel_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fuel_type_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='fuel_type')


class MasterServiceLocation(Base):
    __tablename__ = 'master_service_location'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_service_location_pkey'),
        UniqueConstraint('location_name', name='master_service_location_location_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)

    suppliers: Mapped[list['Suppliers']] = relationship('Suppliers', back_populates='service_location')
    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='service_location')


class MasterStatus(Base):
    __tablename__ = 'master_status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_status_pkey'),
        UniqueConstraint('status_name', name='master_status_status_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    drivers: Mapped[list['Drivers']] = relationship('Drivers', back_populates='status')
    suppliers: Mapped[list['Suppliers']] = relationship('Suppliers', back_populates='status')
    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='status')


class MasterSupplierType(Base):
    __tablename__ = 'master_supplier_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_supplier_type_pkey'),
        UniqueConstraint('supplier_type_name', name='master_supplier_type_supplier_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_type_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    suppliers: Mapped[list['Suppliers']] = relationship('Suppliers', back_populates='supplier_type')


class MasterVehicleMake(Base):
    __tablename__ = 'master_vehicle_make'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_vehicle_make_pkey'),
        UniqueConstraint('make_name', name='master_vehicle_make_make_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    make_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='vehicle_make')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('mobile', name='users_mobile_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150))
    mobile: Mapped[Optional[str]] = mapped_column(String(15))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    mobile_verified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    role: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'user'::character varying"))
    is_blocked: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='user')
    drivers_created_by: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.created_by]', back_populates='users')
    drivers_updated_by: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.updated_by]', back_populates='users_')
    drivers_user: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.user_id]', back_populates='user')
    managers: Mapped[list['Managers']] = relationship('Managers', back_populates='user')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='user')
    reports_download_history: Mapped[list['ReportsDownloadHistory']] = relationship('ReportsDownloadHistory', back_populates='user')
    user_otps: Mapped[list['UserOtps']] = relationship('UserOtps', back_populates='user')
    vehicles_created_by: Mapped[list['Vehicles']] = relationship('Vehicles', foreign_keys='[Vehicles.created_by]', back_populates='users')
    vehicles_updated_by: Mapped[list['Vehicles']] = relationship('Vehicles', foreign_keys='[Vehicles.updated_by]', back_populates='users_')
    parking_locations: Mapped[list['ParkingLocations']] = relationship('ParkingLocations', back_populates='users')
    vehicle_assignment_history: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', back_populates='users')
    vehicle_assignments_created_by: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', foreign_keys='[VehicleAssignments.created_by]', back_populates='users')
    vehicle_assignments_updated_by: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', foreign_keys='[VehicleAssignments.updated_by]', back_populates='users_')


class VehicleDocuments(Base):
    __tablename__ = 'vehicle_documents'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='vehicle_documents_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer)
    document_type: Mapped[Optional[str]] = mapped_column(String(50))
    file_url: Mapped[Optional[str]] = mapped_column(Text)
    expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='audit_logs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='audit_logs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    action: Mapped[Optional[str]] = mapped_column(String(100))
    table_name: Mapped[Optional[str]] = mapped_column(String(100))
    record_id: Mapped[Optional[int]] = mapped_column(Integer)
    old_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    new_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='audit_logs')


class Drivers(Base):
    __tablename__ = 'drivers'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='drivers_created_by_fkey'),
        ForeignKeyConstraint(['status_id'], ['master_status.id'], name='fk_drivers_status'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='drivers_updated_by_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='drivers_user_id_fkey'),
        PrimaryKeyConstraint('id', name='drivers_pkey'),
        UniqueConstraint('aadhaar_number', name='drivers_aadhaar_number_key'),
        UniqueConstraint('driver_code', name='drivers_driver_code_key'),
        UniqueConstraint('license_number', name='drivers_license_number_key'),
        UniqueConstraint('mobile', name='drivers_mobile_key'),
        Index('idx_driver_mobile', 'mobile'),
        Index('idx_license_number', 'license_number')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    driver_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150))
    aadhaar_number: Mapped[Optional[str]] = mapped_column(String(20))
    license_number: Mapped[Optional[str]] = mapped_column(String(100))
    license_expiry: Mapped[Optional[datetime.date]] = mapped_column(Date)
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(20))
    driver_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(150))
    emergency_contact_number: Mapped[Optional[str]] = mapped_column(String(15))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    license_file_url: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    blood_group: Mapped[Optional[str]] = mapped_column(String(10))
    adhaar_url: Mapped[Optional[str]] = mapped_column(String(500))
    status_id: Mapped[Optional[int]] = mapped_column(Integer)

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='drivers_created_by')
    status: Mapped[Optional['MasterStatus']] = relationship('MasterStatus', back_populates='drivers')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='drivers_updated_by')
    user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[user_id], back_populates='drivers_user')
    duty_status: Mapped[list['DutyStatus']] = relationship('DutyStatus', back_populates='driver')
    parking_locations: Mapped[list['ParkingLocations']] = relationship('ParkingLocations', back_populates='driver')
    vehicle_assignment_history_new_driver: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', foreign_keys='[VehicleAssignmentHistory.new_driver_id]', back_populates='new_driver')
    vehicle_assignment_history_old_driver: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', foreign_keys='[VehicleAssignmentHistory.old_driver_id]', back_populates='old_driver')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='driver')


class Managers(Base):
    __tablename__ = 'managers'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='managers_user_id_fkey'),
        PrimaryKeyConstraint('id', name='managers_pkey'),
        UniqueConstraint('manager_code', name='managers_manager_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    manager_code: Mapped[Optional[str]] = mapped_column(String(50))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='managers')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(200))
    message: Mapped[Optional[str]] = mapped_column(Text)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='notifications')


class ReportsDownloadHistory(Base):
    __tablename__ = 'reports_download_history'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='reports_download_history_user_id_fkey'),
        PrimaryKeyConstraint('id', name='reports_download_history_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    report_name: Mapped[Optional[str]] = mapped_column(String(100))
    report_type: Mapped[Optional[str]] = mapped_column(String(50))
    downloaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='reports_download_history')


class Suppliers(Base):
    __tablename__ = 'suppliers'
    __table_args__ = (
        ForeignKeyConstraint(['service_location_id'], ['master_service_location.id'], name='suppliers_service_location_id_fkey'),
        ForeignKeyConstraint(['status_id'], ['master_status.id'], name='suppliers_status_id_fkey'),
        ForeignKeyConstraint(['supplier_type_id'], ['master_supplier_type.id'], name='suppliers_supplier_type_id_fkey'),
        PrimaryKeyConstraint('id', name='suppliers_pkey'),
        UniqueConstraint('aadhaar_number', name='suppliers_aadhaar_number_key'),
        UniqueConstraint('mobile', name='suppliers_mobile_key'),
        UniqueConstraint('supplier_id', name='suppliers_supplier_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[Optional[str]] = mapped_column(String(15))
    alternate_mobile: Mapped[Optional[str]] = mapped_column(String(15))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    aadhaar_number: Mapped[Optional[str]] = mapped_column(String(20))
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    current_address: Mapped[Optional[str]] = mapped_column(Text)
    permanent_address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(10))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    status_id: Mapped[Optional[int]] = mapped_column(Integer)
    supplier_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    service_location_id: Mapped[Optional[int]] = mapped_column(Integer)
    outstanding_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    remarks: Mapped[Optional[str]] = mapped_column(Text)

    service_location: Mapped[Optional['MasterServiceLocation']] = relationship('MasterServiceLocation', back_populates='suppliers')
    status: Mapped[Optional['MasterStatus']] = relationship('MasterStatus', back_populates='suppliers')
    supplier_type: Mapped[Optional['MasterSupplierType']] = relationship('MasterSupplierType', back_populates='suppliers')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='supplier')


class UserOtps(Base):
    __tablename__ = 'user_otps'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_otps_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_otps_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='user_otps')


class Vehicles(Base):
    __tablename__ = 'vehicles'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='vehicles_created_by_fkey'),
        ForeignKeyConstraint(['fuel_issue_id'], ['master_fuel_issue.id'], name='vehicles_fuel_issue_id_fkey'),
        ForeignKeyConstraint(['fuel_type_id'], ['master_fuel_type.id'], name='vehicles_fuel_type_id_fkey'),
        ForeignKeyConstraint(['service_location_id'], ['master_service_location.id'], name='vehicles_service_location_id_fkey'),
        ForeignKeyConstraint(['status_id'], ['master_status.id'], name='vehicles_status_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='vehicles_updated_by_fkey'),
        ForeignKeyConstraint(['vehicle_make_id'], ['master_vehicle_make.id'], name='vehicles_vehicle_make_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicles_pkey'),
        UniqueConstraint('chassis_number', name='vehicles_chassis_number_key'),
        UniqueConstraint('engine_number', name='vehicles_engine_number_key'),
        UniqueConstraint('vehicle_registration_number', name='vehicles_vehicle_registration_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_registration_number: Mapped[str] = mapped_column(String(20), nullable=False)
    service_location_id: Mapped[Optional[int]] = mapped_column(Integer)
    vehicle_make_id: Mapped[Optional[int]] = mapped_column(Integer)
    fuel_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    vehicle_display_number: Mapped[Optional[str]] = mapped_column(String(50))
    average_mileage: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    year_of_make: Mapped[Optional[int]] = mapped_column(Integer)
    engine_number: Mapped[Optional[str]] = mapped_column(String(100))
    chassis_number: Mapped[Optional[str]] = mapped_column(String(100))
    gps_enabled: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    fuel_issue_id: Mapped[Optional[int]] = mapped_column(Integer)
    insurance_company: Mapped[Optional[str]] = mapped_column(String(150))
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100))
    insurance_expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='vehicles_created_by')
    fuel_issue: Mapped[Optional['MasterFuelIssue']] = relationship('MasterFuelIssue', back_populates='vehicles')
    fuel_type: Mapped[Optional['MasterFuelType']] = relationship('MasterFuelType', back_populates='vehicles')
    service_location: Mapped[Optional['MasterServiceLocation']] = relationship('MasterServiceLocation', back_populates='vehicles')
    status: Mapped[Optional['MasterStatus']] = relationship('MasterStatus', back_populates='vehicles')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='vehicles_updated_by')
    vehicle_make: Mapped[Optional['MasterVehicleMake']] = relationship('MasterVehicleMake', back_populates='vehicles')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='vehicle')


class DutyStatus(Base):
    __tablename__ = 'duty_status'
    __table_args__ = (
        ForeignKeyConstraint(['driver_id'], ['drivers.id'], name='duty_status_driver_id_fkey'),
        PrimaryKeyConstraint('id', name='duty_status_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    driver: Mapped[Optional['Drivers']] = relationship('Drivers', back_populates='duty_status')


class ParkingLocations(Base):
    __tablename__ = 'parking_locations'
    __table_args__ = (
        ForeignKeyConstraint(['driver_id'], ['drivers.id'], name='parking_locations_driver_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='parking_locations_updated_by_fkey'),
        PrimaryKeyConstraint('id', name='parking_locations_pkey'),
        Index('idx_parking_vehicle', 'vehicle_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer)
    driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 8))
    longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(11, 8))
    location_name: Mapped[Optional[str]] = mapped_column(Text)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    driver: Mapped[Optional['Drivers']] = relationship('Drivers', back_populates='parking_locations')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='parking_locations')


class VehicleAssignmentHistory(Base):
    __tablename__ = 'vehicle_assignment_history'
    __table_args__ = (
        ForeignKeyConstraint(['assigned_by'], ['users.id'], name='vehicle_assignment_history_assigned_by_fkey'),
        ForeignKeyConstraint(['new_driver_id'], ['drivers.id'], name='vehicle_assignment_history_new_driver_id_fkey'),
        ForeignKeyConstraint(['old_driver_id'], ['drivers.id'], name='vehicle_assignment_history_old_driver_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicle_assignment_history_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer)
    old_driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    new_driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    assigned_by: Mapped[Optional[int]] = mapped_column(Integer)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    changed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='vehicle_assignment_history')
    new_driver: Mapped[Optional['Drivers']] = relationship('Drivers', foreign_keys=[new_driver_id], back_populates='vehicle_assignment_history_new_driver')
    old_driver: Mapped[Optional['Drivers']] = relationship('Drivers', foreign_keys=[old_driver_id], back_populates='vehicle_assignment_history_old_driver')


class VehicleAssignments(Base):
    __tablename__ = 'vehicle_assignments'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='vehicle_assignments_created_by_fkey'),
        ForeignKeyConstraint(['driver_id'], ['drivers.id'], name='vehicle_assignments_driver_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name='fk_vehicle_assignment_supplier'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='vehicle_assignments_updated_by_fkey'),
        ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], name='vehicle_assignments_vehicle_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicle_assignments_pkey'),
        UniqueConstraint('unique_number', name='vehicle_assignments_unique_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    driver_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vehicle_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    assignment_type: Mapped[Optional[str]] = mapped_column(String(50))
    relieved_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    emi_amount: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(12, 2))
    emi_tenure_months: Mapped[Optional[int]] = mapped_column(Integer)
    emi_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    emi_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    transaction_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    unique_number: Mapped[Optional[str]] = mapped_column(String(50))

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='vehicle_assignments_created_by')
    driver: Mapped['Drivers'] = relationship('Drivers', back_populates='vehicle_assignments')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='vehicle_assignments')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='vehicle_assignments_updated_by')
    vehicle: Mapped['Vehicles'] = relationship('Vehicles', back_populates='vehicle_assignments')
    vehicle_emi_transactions: Mapped[list['VehicleEmiTransactions']] = relationship('VehicleEmiTransactions', back_populates='vehicle_assignment')


class VehicleEmiTransactions(Base):
    __tablename__ = 'vehicle_emi_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['vehicle_assignment_id'], ['vehicle_assignments.id'], name='vehicle_emi_transactions_vehicle_assignment_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicle_emi_transactions_pkey'),
        UniqueConstraint('transaction_number', name='vehicle_emi_transactions_transaction_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_assignment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    emi_number: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_number: Mapped[Optional[str]] = mapped_column(String(50))
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    payment_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    payment_status: Mapped[Optional[str]] = mapped_column(String(50))
    transaction_reference: Mapped[Optional[str]] = mapped_column(String(100))
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicle_assignment: Mapped['VehicleAssignments'] = relationship('VehicleAssignments', back_populates='vehicle_emi_transactions')
