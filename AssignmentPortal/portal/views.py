from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('teacher_dashboard')
            return redirect('student_dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'portal/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    # Get all assignments
    assignments = Assignment.objects.all()
    # Get student's submissions
    submissions = Submission.objects.filter(student=request.user)
    # Create a set of assignment IDs that have been submitted
    submitted_assignment_ids = set(submission.assignment.id for submission in submissions)
    
    return render(request, 'portal/student_dashboard.html', {
        'assignments': assignments,
        'submissions': submissions,
        'submitted_assignment_ids': submitted_assignment_ids
    })

@login_required
def teacher_dashboard(request):
    assignments = Assignment.objects.filter(teacher=request.user)
    return render(request, 'portal/teacher_dashboard.html', {'assignments': assignments})

@login_required
def create_assignment(request):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user
            assignment.save()
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm()
    return render(request, 'portal/assignment_create.html', {'form': form})

@login_required
def submit_assignment(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    # Check if student has already submitted
    if Submission.objects.filter(student=request.user, assignment=assignment).exists():
        messages.error(request, 'You have already submitted this assignment')
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.assignment = assignment
            submission.save()
            messages.success(request, 'Assignment submitted successfully')
            return redirect('student_dashboard')
    else:
        form = SubmissionForm()
    return render(request, 'portal/assignment_submit.html', {'form': form, 'assignment': assignment})

@login_required
def view_submissions(request, assignment_id):
    if not request.user.is_staff:
        return redirect('student_dashboard')
    assignment = Assignment.objects.get(id=assignment_id)
    submissions = Submission.objects.filter(assignment=assignment)
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        submission = Submission.objects.get(id=submission_id)
        submission.grade = grade
        submission.feedback = feedback
        submission.save()
        return redirect('view_submissions', assignment_id=assignment_id)
    return render(request, 'portal/submission_view.html', {
        'assignment': assignment,
        'submissions': submissions
    })