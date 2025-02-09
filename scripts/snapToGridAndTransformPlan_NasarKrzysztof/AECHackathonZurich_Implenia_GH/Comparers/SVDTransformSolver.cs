using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.LinearAlgebra.Double;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Comparers
{
    public class SvdTransformSolver
    {
        public Point3d[] Subject { get; }
        public Point3d[] Target { get; }

        public SvdTransformSolver(Point3d[] subject, Point3d[] target)
        {
            if (subject.Length != target.Length || subject.Length < 3) {
                throw new ArgumentException("Subject and target must have the same length and contain at least three points.");
            }

            Subject = subject;
            Target = target;
        }

        public double[,] Solve()
        {
            var centroidSubject = ComputeCentroid(Subject);
            var centroidTarget = ComputeCentroid(Target);

            var normalsSource = Subject.Select(p => CreateVector.DenseOfArray(new double[] { p.X - centroidSubject.X, p.Y - centroidSubject.Y, p.Z - centroidSubject.Z })).ToArray();
            var normalsTarget = Target.Select(p => CreateVector.DenseOfArray(new double[] { p.X - centroidTarget.X, p.Y - centroidTarget.Y, p.Z - centroidTarget.Z })).ToArray();

            var H = CreateMatrix.DenseOfColumnVectors(normalsSource) * CreateMatrix.DenseOfColumnVectors(normalsTarget).Transpose();
            var svd = H.Svd(true);
            var rotation3x3 = svd.VT.Transpose() * svd.U.Transpose();

            if (rotation3x3.Determinant() < 0) // Handle reflection
            {
                var V = svd.VT.Transpose();
                V.SetColumn(2, V.Column(2).Multiply(-1));
                rotation3x3 = V * svd.U.Transpose();
            }

            var translation = -rotation3x3 * CreateVector.DenseOfArray(new double[] { centroidSubject.X, centroidSubject.Y, centroidSubject.Z }) +
                              CreateVector.DenseOfArray(new double[] { centroidTarget.X, centroidTarget.Y, centroidTarget.Z });

            return ConstructTransformationMatrix(rotation3x3, translation);
        }

        private static Point3d ComputeCentroid(Point3d[] points) =>
            points.Aggregate((a, b) => a + b) / points.Length;

        private static double[,] ConstructTransformationMatrix(Matrix<double> rotation, Vector<double> translation)
        {
            var transform = DenseMatrix.CreateIdentity(4);
            for (int i = 0; i < 3; i++) {
                for (int j = 0; j < 3; j++)
                    transform[i, j] = rotation[i, j];
                transform[i, 3] = translation[i];
            }
            return transform.ToArray();
        }
    }

}
