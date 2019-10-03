import random
import time
from string import digits
from bitstring import BitStream

courses = {'CS101A': 40, 'CS101B': 25, 'CS201A': 30, 'CS201B': 30, 'CS191A': 60, 'CS191B': 20,
           'CS291B': 40, 'CS291A': 20, 'CS303': 50, 'CS341': 40, 'CS449': 55, 'CS461': 40}
teachers = {'Hare': ['CS101', 'CS201', 'CS291', 'CS303', 'CS449', 'CS461'],
            'Bingham': ['CS101', 'CS201', 'CS191', 'CS291', 'CS449'],
            'Kuhail': ['CS303', 'CS341'],
            'Mitchell': ['CS191', 'CS291', 'CS303', 'CS341'],
            'Rao': ['CS291', 'CS303', 'CS341', 'CS461']}
times = ['10A', '11A', '12P', '1P', '2P', '3P', '4P']
rooms = {'Haag301': 70, 'Haag206': 30, 'Royall204': 70,
         'Katz209': 50, 'Flarsheim310': 80, 'Flarsheim260': 25, 'Bloch0009': 30}

course_index = 0
teacher_index = 1
time_index = 2
room_index = 3

can_teach_score = 10
room_time = 10
large_enough = 5
capacity_less_than_double = 2
teacher_one_at_a_time = 5
teacher_course_overload = -5
grad_faculty_overload = .95
course_same_time = .90
course_adjacent_time = 1.05
course_adjacent_and_same_building = 5
course_adjacent_and_one_katz = .97
course_adjacent_and_one_bloch = .97
only_one_class = 3


def get_random_parent(population, fit):
    fit_square = [f ** 2 for f in fit]
    probabilities = []
    running_total = 0
    running_probability = 0
    for j in fit_square:
        running_total += j
    for k in fit_square:
        running_probability += (k / running_total)
        probabilities.append(running_probability)

    rand = random.random()
    previous = 0
    for i, probability in enumerate(probabilities):
        if probability > rand > previous:
            return population[i]
        previous = probability


def genetic_function(max_iterations: int, pop_size: int, courses_dict: dict, teachers_dict: dict, times_list: list,
                     rooms_dict: dict):
    number_of_courses = len(courses_dict.keys())
    population = []
    fit = []
    consecutive_bad_generations = 0
    calculated_max_fit = 0
    max_schedule = []
    highest_fitness = []
    for i in range(0, pop_size):
        schedule = []
        for j in range(0, number_of_courses):
            course = []
            course.append(random.choice(list(courses_dict.keys())))
            course.append(random.choice(list(teachers_dict.keys())))
            course.append(random.choice(times_list))
            course.append(random.choice(list(rooms_dict.keys())))
            # print(course)
            schedule.append(course)
        # print(population)
        population.append(schedule)
    fit = fitness(population, pop_size, courses_dict, teachers_dict, times_list, rooms_dict, number_of_courses)
    max_schedule.append(population[fit.index(max(fit))])
    highest_fitness = max(fit)
    calculated_max_fit = max(fit)
    index = 0
    while (index <= max_iterations) and (consecutive_bad_generations < 15):
        last_max_fit = highest_fitness
        print("Generation: ", index)
        new_pop = []
        # crossover
        for i in range(0, pop_size):
            parent_one = population[i]
            parent_two = get_random_parent(population, fit)

            child = []
            child_2 = []

            split_point = random.randint(0, len(parent_one))

            child.append(list(parent_one[0:split_point] + parent_two[split_point:len(parent_two)]))
            # print(child)
            child_2.append(list(parent_two[0:split_point] + parent_one[split_point:len(parent_one)]))
            # print(child_2)
            if fitness(child, 1, courses_dict, teachers_dict, times_list, rooms_dict, number_of_courses)[0] > fitness(child_2, 1, courses_dict, teachers_dict, times_list, rooms_dict, number_of_courses)[0]:
                new_pop.append(child[0])
            else:
                new_pop.append(child_2[0])
            # new_pop.append(child)
        # for i in range(0, pop_size):
        #     # mutation
        #     mutation_selector = random.random()
        #     if mutation_selector < .03:
        #         new_pop[i] = mutate(new_pop[i], number_of_courses, times_list, rooms_dict, teachers_dict)

        population = new_pop.copy()
        new_fit = fitness(new_pop, pop_size, courses_dict, teachers_dict, times_list, rooms_dict, number_of_courses)
        new_max_fit = max(new_fit)
        fit_diff = new_max_fit - last_max_fit
        if (fit_diff / last_max_fit * 100) < .0002:
            consecutive_bad_generations += 1
        else:
            consecutive_bad_generations = 0
        # print("Generation Max Fit: ", new_max_fit)
        fit_average = sum(new_fit) / len(new_fit)
        # print("Average: ", fit_average)
        if new_max_fit > highest_fitness and new_max_fit > calculated_max_fit:
            max_schedule = [new_pop[new_fit.index(max(new_fit))]]
            highest_fitness = new_max_fit
        calculated_max_fit = max(fitness(max_schedule, 1, courses_dict, teachers_dict, times_list, rooms_dict, number_of_courses))
        # print("Max Fit: ", highest_fitness)
        # print("Calculated Max Fit: ", calculated_max_fit)
        # print("Best Schedule", max_schedule[0])
        # print("\n\n")
        index += 1

    print("Max Fit: ", calculated_max_fit)
    return max_schedule[0]


def fitness(pop: list, pop_size: int, courses_dict: dict, teachers_dict: dict, times_list: list, rooms_dict: dict,
            number_of_courses: int):
    fit = []

    for sched in range(0, pop_size):
        fit_score = 0
        current_schedule = pop[sched]
        teacher_course_load_dict_i = teachers_dict.copy()
        teacher_course_load_dict_i = {x: 0 for x in teacher_course_load_dict_i}
        for course_i in range(0, number_of_courses):
            only_class = True
            only_instructor = True
            only_one_course = True
            current_course_i = current_schedule[course_i]
            teacher_course_load_dict_i[current_course_i[teacher_index]] += 1
            # if teacher can teach the course_i
            if can_teach(teachers_dict, current_course_i):
                fit_score += can_teach_score
            if rooms_dict.get(current_course_i[room_index]) > courses_dict.get(current_course_i[course_index]):
                fit_score += large_enough
                if rooms_dict.get(current_course_i[room_index]) < 2 * courses_dict.get(current_course_i[course_index]):
                    fit_score += capacity_less_than_double
            for x in range(0, number_of_courses):
                if course_i != x:
                    # if its not the only course_i in the room at a time
                    if (current_course_i[time_index] == current_schedule[x][time_index]) and (
                            current_course_i[room_index] == current_schedule[x][room_index]):
                        only_class = False
                    if current_course_i[course_index] == current_schedule[x][course_index]:
                        only_one_course = False
                        # if its not the only course_i in the instructor teaches at that time
                    if (current_course_i[time_index] == current_schedule[x][time_index]) and (
                            current_course_i[teacher_index] == current_schedule[x][teacher_index]):
                        only_instructor = False
                    if ((remove_course_section(
                            current_course_i[course_index]) == 'CS101' and remove_course_section(
                        current_schedule[x][course_index]) == 'CS191') or (remove_course_section(
                        current_course_i[course_index]) == 'CS201' and remove_course_section(
                        current_schedule[x][course_index]) == 'CS291')):
                        if (current_course_i[time_index] == current_schedule[x][time_index]):
                            fit_score *= course_same_time
                        if abs(times_list.index(current_course_i[time_index]) - times_list.index(
                                current_schedule[x][time_index])) == 1:
                            fit_score *= course_adjacent_time
                        if remove_numbers(current_course_i[room_index]) == remove_numbers(
                                current_schedule[x][room_index]):
                            fit_score += course_adjacent_and_same_building
                        if remove_numbers(current_course_i[room_index]) == 'Katz' and remove_numbers(
                                current_course_i[room_index]) != 'Katz':
                            fit_score *= course_adjacent_and_one_katz
                        if remove_numbers(current_course_i[room_index]) == 'Bloch' and remove_numbers(
                                current_course_i[room_index]) != 'Bloch':
                            fit_score *= course_adjacent_and_one_bloch

            if only_class:
                fit_score += room_time
            if only_instructor:
                fit_score += teacher_one_at_a_time
            if only_one_course:
                fit_score += only_one_class
        load_diff_i = get_load_diff(teacher_course_load_dict_i)
        if load_diff_i > 0:
            fit_score += teacher_course_overload * load_diff_i
        if get_undergrad_audit(teacher_course_load_dict_i):
            fit_score *= grad_faculty_overload
        if fit_score < 0:
            fit_score = 0
        fit.append(fit_score)
        # print(fit_score)
        # print(teacher_course_load_dict_i)
    return fit


def get_undergrad_audit(teacher_course_load_dict: dict):
    return teacher_course_load_dict['Rao'] > teacher_course_load_dict['Hare'] or teacher_course_load_dict['Rao'] > \
           teacher_course_load_dict['Bingham'] or teacher_course_load_dict['Mitchell'] > teacher_course_load_dict[
               'Hare'] or teacher_course_load_dict['Mitchell'] > teacher_course_load_dict['Bingham']


def remove_course_section(course: str):
    course = course.replace('A', '')
    course = course.replace('B', '')
    return course


def can_teach(teachers_dict: dict, current_course: list):
    return teachers_dict.get(current_course[teacher_index]).__contains__(
        remove_course_section(current_course[course_index]))


def remove_numbers(string):
    remove_digits = str.maketrans('', '', digits)
    return string.translate(remove_digits)


def get_load_diff(teacher_course_load_dict: dict):
    total_load_diff = 0
    for load in teacher_course_load_dict.values():
        if load > 4:
            total_load_diff += (load - 4)
    return total_load_diff


def mutate(schedule: list, num_courses: int, times: list, rooms: dict, teachers: dict):
    sched = schedule[:]
    time = times[random.randint(0, len(times) - 1)]
    room = list(rooms.keys())[random.randint(0, len(rooms.keys()) - 1)]
    teacher = list(teachers.keys())[random.randint(0, len(teachers) - 1)]
    course = random.randint(0, num_courses - 1)

    mutation_variable = random.randint(0, 2)

    if mutation_variable == 0:
        sched[course][time_index] = time
    if mutation_variable == 1:
        sched[course][room_index] = room
    if mutation_variable == 2:
        sched[course][teacher_index] = teacher

    return sched


if __name__ == "__main__":
    best_schedule = genetic_function(200, 400, courses, teachers, times, rooms)
    print(best_schedule)

    # report
    teacher_course_load_dict = teachers.copy()
    teacher_course_load_dict = {x: 0 for x in teacher_course_load_dict}
    for course in range(0, len(best_schedule)):
        current_course = best_schedule[course]
        teacher_course_load_dict[current_course[teacher_index]] += 1
        # if teacher can teach the course
        if not can_teach(teachers, current_course):
            print("Teacher cannot teach class violation")
        if rooms.get(current_course[room_index]) < courses.get(current_course[course_index]):
            print("Room too small violation")
        for x in range(0, len(best_schedule)):
            compare_course = best_schedule[x]
            if course != x:
                # if its not the only course in the room at a time
                if (current_course[time_index] == compare_course[time_index]) and (
                        current_course[room_index] == compare_course[room_index]):
                    print("More than one class in a room")
        load_diff = get_load_diff(teacher_course_load_dict)
        if load_diff > 0:
            print("Teacher teaching more than 4 class violation")
