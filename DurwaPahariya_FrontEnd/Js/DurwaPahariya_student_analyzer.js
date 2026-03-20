const students = [
  {
    name: "Lalit",
    marks: [
      { subject: "Math", score: 78 },
      { subject: "English", score: 82 },
      { subject: "Science", score: 74 },
      { subject: "History", score: 69 },
      { subject: "Computer", score: 88 }
    ],
    attendance: 82
  },
  {
    name: "Rahul",
    marks: [
      { subject: "Math", score: 90 },
      { subject: "English", score: 85 },
      { subject: "Science", score: 80 },
      { subject: "History", score: 76 },
      { subject: "Computer", score: 92 }
    ],

    attendance: 91
  },
 
];

//1) Calculation: TOTAL MARKS

function calculateTotalMarks(student) {
  let total = 0;
  for (let sub of student.marks) {
    total += sub.score;
  }
  return total;
}
//console.log("Total marks scored by Lalit:", calculateTotalMarks(students[0]));
//console.log("Total marks scored by Rahul:", calculateTotalMarks(students[1]));

//2)Calculation: AVERAGE MARKS

function calculateAverageMarks(student){
    const total = calculateTotalMarks(student);
    
    return total/student.marks.length;
}
//console.log("Avg marks scored by Lalit:", calculateAverageMarks(students[0]));
//console.log("Avg marks scored by Rahul:", calculateAverageMarks(students[1]));

// Subject-wise Highest Marks 
function subjectHighestScore(students) {
  const subjects = students[0].marks.map(m => m.subject);

  subjects.forEach(subject => {
    const { topper, highest } = students.reduce(
      (acc, student) => {
        const sub = student.marks.find(m => m.subject === subject);
        if (sub.score > acc.highest) {
          acc.highest = sub.score;
          acc.topper = student.name;
        }
        return acc;
      },
      { topper: "", highest: 0 }
    );

   // console.log(`Highest in ${subject}: ${topper} (${highest})`);
  });
}
subjectHighestScore(students);

//Subject Average

function subjectAverageMarks(students) {

    let subjects = students[0].marks.map(m => m.subject);

    subjects.forEach(subject => {

        let total = 0;

        students.forEach(student => {
            let sub = student.marks.find(m => m.subject === subject);
            total += sub.score;
        });

        let avg = total / students.length;

        console.log(`Average ${subject} Score: ${avg}`);
    });
}

subjectAverageMarks(students);