using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Rhino.Geometry;
using Rhino;

namespace AECHackathonZurich_Implenia_GH.Comparers
{
    public class IcpSolver
    {
        private readonly Point3d[] _subject;
        private readonly Point3d[] _target;
        private readonly Vector3d _subjectToOrigin;
        private readonly Vector3d _subjectToTarget;
        private readonly Vector3d _targetToOrigin;
        private HashSet<int> _takenTargetIndices;

        public IcpSolver(Point3d[] subject, Point3d[] target)
        {
            var centroidSubject = subject.Aggregate((a, b) => a + b) / subject.Length;
            var centroidTarget = target.Aggregate((a, b) => a + b) / target.Length;

            _subjectToOrigin = -1 * (Vector3d)centroidSubject;
            _targetToOrigin = -1 * (Vector3d)centroidTarget;
            _subjectToTarget = centroidSubject - centroidTarget;

            _subject = subject.Select(pt => pt + _subjectToOrigin).ToArray();
            _target = target.Select(pt => pt + _targetToOrigin).ToArray();
        }

        public Transform Solve(int iterations, double convergenceThreshold, out int performedIterations)
        {
            iterations = Math.Max(1, iterations);
            var s = (Point3d[])_subject.Clone();
            var tSteps = new List<Transform>();

            performedIterations = 0;
            for (; performedIterations < iterations; performedIterations++) {
                _takenTargetIndices = new HashSet<int>();
                var targetClosest = s.Select(ClosestTargetPointExcludeDoubling).ToArray();

                var solver = new SvdTransformSolver(s, targetClosest);
                var result = solver.Solve();
                var t = TransformFromMatrix(result);
                tSteps.Add(t);

                foreach (var point in s)
                    point.Transform(t);

                if (IsTransformIdentity(result, convergenceThreshold)) {
                    performedIterations++;
                    break;
                }
            }

            return ComputeFinalTransform(tSteps);
        }

        public Transform Solve(int iterations, double convergenceThreshold) => Solve(iterations, convergenceThreshold, out _);

        private Transform ComputeFinalTransform(List<Transform> tSteps)
        {
            var moveBackToTarget = Transform.Translation(-1 * _targetToOrigin);
            var subjectToOrigin = Transform.Translation(_subjectToOrigin);

            tSteps.Reverse();
            return tSteps.Aggregate(moveBackToTarget, (current, step) => current * step) * subjectToOrigin;
        }

        private bool IsTransformIdentity(double[,] matrix, double tolerance)
        {
            for (int i = 0; i < matrix.GetLength(0); i++) {
                for (int j = 0; j < matrix.GetLength(1); j++) {
                    double expected = i == j ? 1 : 0;
                    if (!RhinoMath.EpsilonEquals(matrix[i, j], expected, tolerance))
                        return false;
                }
            }
            return true;
        }

        private Point3d ClosestTargetPointExcludeDoubling(Point3d candidate)
        {
            int bestIndex = -1;
            var closestPt = _target[0];
            double minDist = double.MaxValue;

            for (int i = 0; i < _target.Length; i++) {
                if (_takenTargetIndices.Contains(i)) continue;

                double dist = _target[i].DistanceToSquared(candidate);
                if (dist < minDist) {
                    closestPt = _target[i];
                    minDist = dist;
                    bestIndex = i;
                }
            }

            if (bestIndex != -1)
                _takenTargetIndices.Add(bestIndex);

            return closestPt;
        }

        private Transform TransformFromMatrix(double[,] matrix)
        {
            var transform = Transform.Identity;
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 4; j++) {
                    transform[i, j] = matrix[i, j];
                }
            }
            return transform;
        }
    }
}
