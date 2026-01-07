"""Create school command."""

from src.application.common.base_use_case import UseCase
from src.application.common.unit_of_work import IUnitOfWork
from src.application.features.schools.dtos import CreateSchoolInput, SchoolOutput
from src.domain.entities.school import School


class CreateSchoolCommand(UseCase[CreateSchoolInput, SchoolOutput]):
    """Use case for creating a new school."""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def execute(self, input_dto: CreateSchoolInput) -> SchoolOutput:
        """Create a new school."""
        async with self.uow:
            school = School(
                name=input_dto.name,
                address=input_dto.address,
                city=input_dto.city,
                state=input_dto.state,
                country=input_dto.country,
                phone_number=input_dto.phone_number,
                email=input_dto.email,
            )

            created_school = await self.uow.schools.create(school)
            await self.uow.commit()

            return SchoolOutput(
                id=created_school.id,
                name=created_school.name,
                address=created_school.address,
                city=created_school.city,
                state=created_school.state,
                country=created_school.country,
                phone_number=created_school.phone_number,
                email=created_school.email,
                is_active=created_school.is_active,
                teacher_count=created_school.teacher_count,
                student_count=created_school.student_count,
                created_at=created_school.created_at,
            )
