
from typing import Optional
import datetime
import decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
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


t_dashboard_summary_mat = Table(
    'dashboard_summary_mat', Base.metadata,
    Column('row_id', Integer),
    Column('total_drivers', BigInteger),
    Column('total_vehicles', BigInteger),
    Column('assigned_vehicles', BigInteger),
    Column('unassigned_vehicles', BigInteger),
    Column('active_drivers', BigInteger),
    Column('inactive_drivers', BigInteger),
    Column('outstanding_amount', Numeric)
)


class MasterBranch(Base):
    __tablename__ = 'master_branch'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_branch_pkey'),
        UniqueConstraint('branch_name', name='master_branch_branch_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_name: Mapped[str] = mapped_column(String(150), nullable=False)
    location_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    suppliers: Mapped[list['Suppliers']] = relationship('Suppliers', back_populates='branch')
    users: Mapped[list['Users']] = relationship('Users', back_populates='branch')
    drivers: Mapped[list['Drivers']] = relationship('Drivers', back_populates='branch')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='branch')


class MasterCompany(Base):
    __tablename__ = 'master_company'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_company_pkey'),
        UniqueConstraint('company_name', name='master_company_company_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='company')


class MasterFuelIssue(Base):
    __tablename__ = 'master_fuel_issue'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_fuel_issue_pkey'),
        UniqueConstraint('fuel_issue_name', name='master_fuel_issue_fuel_issue_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fuel_issue_name: Mapped[str] = mapped_column(String(50), nullable=False)

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='fuel_issue')


class MasterFuelType(Base):
    __tablename__ = 'master_fuel_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_fuel_type_pkey'),
        UniqueConstraint('fuel_type_name', name='master_fuel_type_fuel_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fuel_type_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class MasterRoles(Base):
    __tablename__ = 'master_roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_roles_pkey'),
        UniqueConstraint('role_name', name='master_roles_role_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped[list['Users']] = relationship('Users', back_populates='role')


class MasterServiceLocation(Base):
    __tablename__ = 'master_service_location'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_service_location_pkey'),
        UniqueConstraint('location_name', name='master_service_location_location_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='service_location')


class MasterStatus(Base):
    __tablename__ = 'master_status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_status_pkey'),
        UniqueConstraint('status_name', name='master_status_status_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class MasterSupplierType(Base):
    __tablename__ = 'master_supplier_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_supplier_type_pkey'),
        UniqueConstraint('supplier_type_name', name='master_supplier_type_supplier_type_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_type_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    suppliers: Mapped[list['Suppliers']] = relationship('Suppliers', back_populates='supplier_type')
    drivers: Mapped[list['Drivers']] = relationship('Drivers', back_populates='supplier_type')


class MasterTaxStatus(Base):
    __tablename__ = 'master_tax_status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_tax_status_pkey'),
        UniqueConstraint('tax_status_name', name='master_tax_status_tax_status_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tax_status_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='tax_status')


class MasterTransmissionType(Base):
    __tablename__ = 'master_transmission_type'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_transmission_type_pkey'),
        UniqueConstraint('transmission_name', name='master_transmission_type_transmission_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transmission_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='transmission_type')


class MasterVehicleMake(Base):
    __tablename__ = 'master_vehicle_make'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_vehicle_make_pkey'),
        UniqueConstraint('make_name', name='master_vehicle_make_make_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    make_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class MasterVehicleModel(Base):
    __tablename__ = 'master_vehicle_model'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='master_vehicle_model_pkey'),
        UniqueConstraint('model_name', name='master_vehicle_model_model_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_make_id: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', back_populates='vehicle_model')


class VehicleDocuments(Base):
    __tablename__ = 'vehicle_documents'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='vehicle_documents_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer)
    document_type: Mapped[Optional[str]] = mapped_column(String(50))
    file_url: Mapped[Optional[str]] = mapped_column(Text)
    expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class Suppliers(Base):
    __tablename__ = 'suppliers'
    __table_args__ = (
        CheckConstraint("agreement_status::text = ANY (ARRAY['Completed'::character varying, 'Not Completed'::character varying]::text[])", name='chk_suppliers_agreement_status'),
        CheckConstraint('agreement_tenure_months IS NULL OR agreement_tenure_months < 48', name='chk_suppliers_agreement_tenure'),
        CheckConstraint("character_nature::text = ANY (ARRAY['Excellent'::character varying, 'Very Good'::character varying, 'Good'::character varying, 'Fair'::character varying, 'Poor'::character varying]::text[])", name='chk_suppliers_character_nature'),
        ForeignKeyConstraint(['branch_id'], ['master_branch.id'], name='fk_suppliers_branch'),
        ForeignKeyConstraint(['supplier_type_id'], ['master_supplier_type.id'], name='suppliers_supplier_type_id_fkey'),
        PrimaryKeyConstraint('id', name='suppliers_pkey'),
        UniqueConstraint('aadhaar_number', name='suppliers_aadhaar_number_key'),
        UniqueConstraint('mobile', name='suppliers_mobile_key'),
        UniqueConstraint('supplier_id', name='suppliers_supplier_id_key'),
        Index('idx_suppliers_branch_id', 'branch_id'),
        Index('idx_suppliers_outstanding', 'outstanding_amount'),
        Index('idx_suppliers_service_location_id', 'service_location_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[str] = mapped_column(String(50), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)
    permanent_address: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    temporary_address: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    reference_person_name: Mapped[str] = mapped_column(String(150), nullable=False, server_default=text("''::character varying"))
    reference_contact_number_1: Mapped[str] = mapped_column(String(15), nullable=False, server_default=text("''::character varying"))
    reference_contact_number_2: Mapped[str] = mapped_column(String(15), nullable=False, server_default=text("''::character varying"))
    emergency_contact_name: Mapped[str] = mapped_column(String(150), nullable=False, server_default=text("''::character varying"))
    emergency_contact_number: Mapped[str] = mapped_column(String(15), nullable=False, server_default=text("''::character varying"))
    character_nature: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'Good'::character varying"))
    alternate_mobile: Mapped[Optional[str]] = mapped_column(String(15))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    aadhaar_number: Mapped[Optional[str]] = mapped_column(String(20))
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    current_address: Mapped[Optional[str]] = mapped_column(Text)
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
    supplier_code: Mapped[Optional[str]] = mapped_column(String(50))
    branch_id: Mapped[Optional[int]] = mapped_column(Integer)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10))
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(Date)
    adhaar_url: Mapped[Optional[str]] = mapped_column(Text)
    license_number: Mapped[Optional[str]] = mapped_column(String(100))
    license_expiry: Mapped[Optional[datetime.date]] = mapped_column(Date)
    license_file_url: Mapped[Optional[str]] = mapped_column(Text)
    pancard_number: Mapped[Optional[str]] = mapped_column(String(20))
    pancard_file_url: Mapped[Optional[str]] = mapped_column(Text)
    bank_passbook_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    gas_bill_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    electricity_bill_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    joining_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    agreement_start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    agreement_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    agreement_status: Mapped[Optional[str]] = mapped_column(String(20))
    emi_completed_months: Mapped[Optional[int]] = mapped_column(Integer)
    agreement_tenure_months: Mapped[Optional[int]] = mapped_column(Integer)

    branch: Mapped[Optional['MasterBranch']] = relationship('MasterBranch', back_populates='suppliers')
    supplier_type: Mapped[Optional['MasterSupplierType']] = relationship('MasterSupplierType', back_populates='suppliers')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='supplier')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("status::text = ANY (ARRAY['Active'::character varying, 'Deactive'::character varying, 'Block Listed'::character varying]::text[])", name='users_status_check'),
        ForeignKeyConstraint(['branch_id'], ['master_branch.id'], ondelete='SET NULL', name='users_branch_id_fkey'),
        ForeignKeyConstraint(['role_id'], ['master_roles.id'], name='users_role_id_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('mobile', name='users_mobile_key'),
        UniqueConstraint('staff_code', name='users_staff_code_key'),
        Index('idx_users_branch_id', 'branch_id'),
        Index('idx_users_staff_code', 'staff_code')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    email: Mapped[Optional[str]] = mapped_column(String(150))
    mobile: Mapped[Optional[str]] = mapped_column(String(15))
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    mobile_verified: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    is_blocked: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    service_state: Mapped[Optional[str]] = mapped_column(String(100))
    branch_id: Mapped[Optional[int]] = mapped_column(Integer)
    staff_code: Mapped[Optional[str]] = mapped_column(String(50))
    designation: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'Active'::character varying"))
    active_session_token: Mapped[Optional[str]] = mapped_column(String(64))
    login_attempt_count: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))

    branch: Mapped[Optional['MasterBranch']] = relationship('MasterBranch', back_populates='users')
    role: Mapped['MasterRoles'] = relationship('MasterRoles', back_populates='users')
    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='user')
    drivers: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.created_by]', back_populates='users')
    drivers_: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.updated_by]', back_populates='users_')
    drivers1: Mapped[list['Drivers']] = relationship('Drivers', foreign_keys='[Drivers.user_id]', back_populates='user')
    managers: Mapped[list['Managers']] = relationship('Managers', back_populates='user')
    messages: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.receiver_id]', back_populates='receiver')
    messages_: Mapped[list['Messages']] = relationship('Messages', foreign_keys='[Messages.sender_id]', back_populates='sender')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='user')
    reports_download_history: Mapped[list['ReportsDownloadHistory']] = relationship('ReportsDownloadHistory', back_populates='user')
    staff_permissions: Mapped[list['StaffPermissions']] = relationship('StaffPermissions', back_populates='user')
    user_otps: Mapped[list['UserOtps']] = relationship('UserOtps', back_populates='user')
    vehicles: Mapped[list['Vehicles']] = relationship('Vehicles', foreign_keys='[Vehicles.created_by]', back_populates='users')
    vehicles_: Mapped[list['Vehicles']] = relationship('Vehicles', foreign_keys='[Vehicles.updated_by]', back_populates='users_')
    parking_locations: Mapped[list['ParkingLocations']] = relationship('ParkingLocations', back_populates='users')
    vehicle_assignment_history: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', back_populates='users')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', foreign_keys='[VehicleAssignments.created_by]', back_populates='users')
    vehicle_assignments_: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', foreign_keys='[VehicleAssignments.updated_by]', back_populates='users_')


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='audit_logs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='audit_logs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
        CheckConstraint("character_nature::text = ANY (ARRAY['Excellent'::character varying, 'Very Good'::character varying, 'Good'::character varying, 'Fair'::character varying, 'Poor'::character varying]::text[])", name='chk_character_nature'),
        ForeignKeyConstraint(['branch_id'], ['master_branch.id'], name='fk_drivers_branch'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='drivers_created_by_fkey'),
        ForeignKeyConstraint(['supplier_type_id'], ['master_supplier_type.id'], name='fk_drivers_supplier_type'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='drivers_updated_by_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='drivers_user_id_fkey'),
        PrimaryKeyConstraint('id', name='drivers_pkey'),
        UniqueConstraint('aadhaar_number', name='drivers_aadhaar_number_key'),
        UniqueConstraint('driver_code', name='drivers_driver_code_key'),
        UniqueConstraint('license_number', name='drivers_license_number_key'),
        UniqueConstraint('mobile', name='drivers_mobile_key'),
        Index('idx_driver_mobile', 'mobile'),
        Index('idx_drivers_license_expiry', 'license_expiry'),
        Index('idx_license_number', 'license_number')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_code: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False)
    permanent_address: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    temporary_address: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    reference_person_name: Mapped[str] = mapped_column(String(150), nullable=False, server_default=text("''::character varying"))
    reference_contact_number_1: Mapped[str] = mapped_column(String(15), nullable=False, server_default=text("''::character varying"))
    reference_contact_number_2: Mapped[str] = mapped_column(String(15), nullable=False, server_default=text("''::character varying"))
    character_nature: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'Good'::character varying"))
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
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    branch_id: Mapped[Optional[int]] = mapped_column(Integer)
    pancard_number: Mapped[Optional[str]] = mapped_column(String(20))
    pancard_file_url: Mapped[Optional[str]] = mapped_column(Text)
    gas_bill_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    electricity_bill_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    bank_passbook_photo_url: Mapped[Optional[str]] = mapped_column(Text)
    supplier_type_id: Mapped[Optional[int]] = mapped_column(Integer)

    branch: Mapped[Optional['MasterBranch']] = relationship('MasterBranch', back_populates='drivers')
    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='drivers')
    supplier_type: Mapped[Optional['MasterSupplierType']] = relationship('MasterSupplierType', back_populates='drivers')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='drivers_')
    user: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[user_id], back_populates='drivers1')
    duty_status: Mapped[list['DutyStatus']] = relationship('DutyStatus', back_populates='driver')
    parking_locations: Mapped[list['ParkingLocations']] = relationship('ParkingLocations', back_populates='driver')
    vehicle_assignment_history: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', foreign_keys='[VehicleAssignmentHistory.new_driver_id]', back_populates='new_driver')
    vehicle_assignment_history_: Mapped[list['VehicleAssignmentHistory']] = relationship('VehicleAssignmentHistory', foreign_keys='[VehicleAssignmentHistory.old_driver_id]', back_populates='old_driver')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='driver')


class Managers(Base):
    __tablename__ = 'managers'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='managers_user_id_fkey'),
        PrimaryKeyConstraint('id', name='managers_pkey'),
        UniqueConstraint('manager_code', name='managers_manager_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    manager_code: Mapped[Optional[str]] = mapped_column(String(50))
    department: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='managers')


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        ForeignKeyConstraint(['receiver_id'], ['users.id'], name='messages_receiver_id_fkey'),
        ForeignKeyConstraint(['sender_id'], ['users.id'], name='messages_sender_id_fkey'),
        PrimaryKeyConstraint('id', name='messages_pkey'),
        Index('idx_messages_receiver_sender', 'receiver_id', 'sender_id'),
        Index('idx_messages_sender_receiver', 'sender_id', 'receiver_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(Integer, nullable=False)
    receiver_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    receiver: Mapped['Users'] = relationship('Users', foreign_keys=[receiver_id], back_populates='messages')
    sender: Mapped['Users'] = relationship('Users', foreign_keys=[sender_id], back_populates='messages_')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    report_name: Mapped[Optional[str]] = mapped_column(String(100))
    report_type: Mapped[Optional[str]] = mapped_column(String(50))
    downloaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='reports_download_history')


class StaffPermissions(Base):
    __tablename__ = 'staff_permissions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='staff_permissions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='staff_permissions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    messages: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    dashboard: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    drivers: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    vehicles: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    suppliers: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    assignments: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    reports: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    settings: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    staff_management: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    user: Mapped['Users'] = relationship('Users', back_populates='staff_permissions')


class UserOtps(Base):
    __tablename__ = 'user_otps'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_otps_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_otps_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='user_otps')


class Vehicles(Base):
    __tablename__ = 'vehicles'
    __table_args__ = (
        ForeignKeyConstraint(['company_id'], ['master_company.id'], name='vehicles_company_id_fkey'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='vehicles_created_by_fkey'),
        ForeignKeyConstraint(['fuel_issue_id'], ['master_fuel_issue.id'], name='vehicles_fuel_issue_id_fkey'),
        ForeignKeyConstraint(['tax_status_id'], ['master_tax_status.id'], name='vehicles_tax_status_id_fkey'),
        ForeignKeyConstraint(['transmission_type_id'], ['master_transmission_type.id'], name='vehicles_transmission_type_id_fkey'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='vehicles_updated_by_fkey'),
        ForeignKeyConstraint(['vehicle_model_id'], ['master_vehicle_model.id'], name='vehicles_vehicle_model_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicles_pkey'),
        UniqueConstraint('chassis_number', name='vehicles_chassis_number_key'),
        UniqueConstraint('engine_number', name='vehicles_engine_number_key'),
        UniqueConstraint('vehicle_registration_number', name='vehicles_vehicle_registration_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
    status_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    vehicle_model_id: Mapped[Optional[int]] = mapped_column(Integer)
    seating_capacity: Mapped[Optional[int]] = mapped_column(Integer)
    registration_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    vehicle_photo: Mapped[Optional[str]] = mapped_column(String(500))
    transmission_type_id: Mapped[Optional[int]] = mapped_column(Integer)
    tax_status_id: Mapped[Optional[int]] = mapped_column(Integer)
    company_id: Mapped[Optional[int]] = mapped_column(Integer)

    company: Mapped[Optional['MasterCompany']] = relationship('MasterCompany', back_populates='vehicles')
    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='vehicles')
    fuel_issue: Mapped[Optional['MasterFuelIssue']] = relationship('MasterFuelIssue', back_populates='vehicles')
    tax_status: Mapped[Optional['MasterTaxStatus']] = relationship('MasterTaxStatus', back_populates='vehicles')
    transmission_type: Mapped[Optional['MasterTransmissionType']] = relationship('MasterTransmissionType', back_populates='vehicles')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='vehicles_')
    vehicle_model: Mapped[Optional['MasterVehicleModel']] = relationship('MasterVehicleModel', back_populates='vehicles')
    vehicle_assignments: Mapped[list['VehicleAssignments']] = relationship('VehicleAssignments', back_populates='vehicle')


class DutyStatus(Base):
    __tablename__ = 'duty_status'
    __table_args__ = (
        ForeignKeyConstraint(['driver_id'], ['drivers.id'], name='duty_status_driver_id_fkey'),
        PrimaryKeyConstraint('id', name='duty_status_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(Integer)
    old_driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    new_driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    assigned_by: Mapped[Optional[int]] = mapped_column(Integer)
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    changed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='vehicle_assignment_history')
    new_driver: Mapped[Optional['Drivers']] = relationship('Drivers', foreign_keys=[new_driver_id], back_populates='vehicle_assignment_history')
    old_driver: Mapped[Optional['Drivers']] = relationship('Drivers', foreign_keys=[old_driver_id], back_populates='vehicle_assignment_history_')


class VehicleAssignments(Base):
    __tablename__ = 'vehicle_assignments'
    __table_args__ = (
        ForeignKeyConstraint(['branch_id'], ['master_branch.id'], name='vehicle_assignments_branch_id_fkey'),
        ForeignKeyConstraint(['created_by'], ['users.id'], name='vehicle_assignments_created_by_fkey'),
        ForeignKeyConstraint(['driver_id'], ['drivers.id'], name='vehicle_assignments_driver_id_fkey'),
        ForeignKeyConstraint(['service_location_id'], ['master_service_location.id'], name='vehicle_assignments_service_location_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name='fk_vehicle_assignment_supplier'),
        ForeignKeyConstraint(['updated_by'], ['users.id'], name='vehicle_assignments_updated_by_fkey'),
        ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], name='vehicle_assignments_vehicle_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicle_assignments_pkey'),
        UniqueConstraint('unique_number', name='vehicle_assignments_unique_number_key'),
        Index('idx_vehicle_assignments_assigned_date', 'assigned_date'),
        Index('idx_vehicle_assignments_driver_id', 'driver_id'),
        Index('idx_vehicle_assignments_vehicle_id', 'vehicle_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    driver_id: Mapped[Optional[int]] = mapped_column(Integer)
    assignment_type: Mapped[Optional[str]] = mapped_column(String(50))
    relieved_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    is_active: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))
    remarks: Mapped[Optional[str]] = mapped_column(Text)
    created_by: Mapped[Optional[int]] = mapped_column(Integer)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    transaction_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    unique_number: Mapped[Optional[str]] = mapped_column(String(50))
    service_location_id: Mapped[Optional[int]] = mapped_column(Integer)
    branch_id: Mapped[Optional[int]] = mapped_column(Integer)
    vehicle_odometer_km: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 2))
    allotment_document_photo: Mapped[Optional[str]] = mapped_column(Text)
    vehicle_photo_front: Mapped[Optional[str]] = mapped_column(Text)
    vehicle_photo_back: Mapped[Optional[str]] = mapped_column(Text)
    vehicle_photo_left: Mapped[Optional[str]] = mapped_column(Text)
    vehicle_photo_right: Mapped[Optional[str]] = mapped_column(Text)

    branch: Mapped[Optional['MasterBranch']] = relationship('MasterBranch', back_populates='vehicle_assignments')
    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[created_by], back_populates='vehicle_assignments')
    driver: Mapped[Optional['Drivers']] = relationship('Drivers', back_populates='vehicle_assignments')
    service_location: Mapped[Optional['MasterServiceLocation']] = relationship('MasterServiceLocation', back_populates='vehicle_assignments')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='vehicle_assignments')
    users_: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[updated_by], back_populates='vehicle_assignments_')
    vehicle: Mapped['Vehicles'] = relationship('Vehicles', back_populates='vehicle_assignments')
    vehicle_emi_transactions: Mapped[list['VehicleEmiTransactions']] = relationship('VehicleEmiTransactions', back_populates='vehicle_assignment')


class VehicleEmiTransactions(Base):
    __tablename__ = 'vehicle_emi_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['vehicle_assignment_id'], ['vehicle_assignments.id'], name='vehicle_emi_transactions_vehicle_assignment_id_fkey'),
        PrimaryKeyConstraint('id', name='vehicle_emi_transactions_pkey'),
        UniqueConstraint('transaction_number', name='vehicle_emi_transactions_transaction_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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
