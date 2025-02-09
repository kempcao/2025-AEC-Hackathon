using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using MathNet.Numerics;
using MathNet.Numerics.LinearAlgebra;
using MathNet.Numerics.LinearAlgebra.Double;

using Rhino.Collections;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Comparers
{
    public static class WeightedSVDAlignment
    {
        public static Transform AlignPointsWeighted(
            List<LabeledPoint> sourcePoints,
            List<LabeledPoint> targetPoints, 
            int internalIterations)
        {
            var sourceGroups = sourcePoints.GroupBy(p => p.Label).ToDictionary(g => g.Key, g => g.ToList());
            var targetGroups = targetPoints.GroupBy(p => p.Label).ToDictionary(g => g.Key, g => g.ToList());

                var transforms = new List<Transform>();
                var weights = new List<double>();

                foreach (var label in sourceGroups.Keys.Intersect(targetGroups.Keys)) {
                    var src = sourceGroups[label].Select(p => p.Position).ToArray();
                    var tgt = targetGroups[label].Select(p => p.Position).ToArray();

                    IcpSolver solver = new IcpSolver(src, tgt);
                    var transform = solver.Solve(internalIterations, 0.0000001);

                    transforms.Add(transform);
                    weights.Add(src.Length);
                }

            return WeightedAverageTransform(transforms, weights);
            //return WeightedAverageTransformV2(transforms, weights);
        }

        public static Transform WeightedAverageTransform(List<Transform> transforms, List<double> weights)
        {
            double weightSum = 0;
            for (int i = 0; i < weights.Count; i++)
                weightSum += weights[i];
            for (int i = 0; i < weights.Count; i++)
                weights[i] /= weightSum;

            Vector3d weightedTranslation = new Vector3d(0, 0, 0);
            for (int i = 0; i < transforms.Count; i++) {
                Vector3d translation = new Vector3d(transforms[i].M03, transforms[i].M13, transforms[i].M23);
                weightedTranslation += translation * weights[i];
            }

            List<Quaternion> quaternions = new List<Quaternion>();
            for (int i = 0; i < transforms.Count; i++) {
                Transform rotationOnly = transforms[i];
                rotationOnly.M03 = rotationOnly.M13 = rotationOnly.M23 = 0;

                Quaternion q;
                if (rotationOnly.GetQuaternion(out q)) {
                    quaternions.Add(q);
                }
                else {
                    throw new InvalidOperationException("Can't get quaternion from the transform matrix.");
                }
            }

            Quaternion avgQuaternion = new Quaternion(0, 0, 0, 0);
            for (int i = 0; i < quaternions.Count; i++) {
                avgQuaternion = new Quaternion(
                    avgQuaternion.A + quaternions[i].A * weights[i],
                    avgQuaternion.B + quaternions[i].B * weights[i],
                    avgQuaternion.C + quaternions[i].C * weights[i],
                    avgQuaternion.D + quaternions[i].D * weights[i]
                );
            }
            avgQuaternion.Unitize();

            Transform resultRotation = Transform.Identity;
            avgQuaternion.GetRotation(out double angle, out Vector3d axis);
            resultRotation = Transform.Rotation(angle, axis, Point3d.Origin);

            Transform resultTransform = resultRotation;
            resultTransform.M03 = weightedTranslation.X;
            resultTransform.M13 = weightedTranslation.Y;
            resultTransform.M23 = weightedTranslation.Z;

            return resultTransform;
        }

        /// <summary>
        /// Another approach...
        /// </summary>
        /// <param name="transforms"></param>
        /// <param name="weights"></param>
        /// <returns></returns>
        /// <exception cref="ArgumentException"></exception>
        /// <exception cref="InvalidOperationException"></exception>
        public static Transform WeightedAverageTransformV2(List<Transform> transforms, List<double> weights)
        {
            double weightSum = weights.Sum();
            if (weightSum == 0)
                throw new ArgumentException("The sum of weights cannot be zero.");
            weights = weights.Select(w => w / weightSum).ToList();

            Vector3d weightedTranslation = Vector3d.Zero;
            for (int i = 0; i < transforms.Count; i++) {
                Vector3d translation = new Vector3d(transforms[i].M03, transforms[i].M13, transforms[i].M23);
                weightedTranslation += translation * weights[i];
            }

            List<Quaternion> quaternions = new List<Quaternion>();
            for (int i = 0; i < transforms.Count; i++) {
                Transform rotationOnly = transforms[i];
                rotationOnly.M03 = rotationOnly.M13 = rotationOnly.M23 = 0;

                Quaternion q;
                if (rotationOnly.GetQuaternion(out q)) {
                    quaternions.Add(q);
                }
                else {
                    throw new InvalidOperationException("Can't get quaternion from the transform matrix.");
                }
            }

            // Compute weighted quaternion average using custom SLERP
            Quaternion avgQuaternion = quaternions[0];
            for (int i = 1; i < quaternions.Count; i++) {
                avgQuaternion = Slerp(avgQuaternion, quaternions[i], weights[i]);
            }
            avgQuaternion.Unitize(); // Ensure valid quaternion

            Transform resultRotation = Transform.Identity;
            avgQuaternion.GetRotation(out double angle, out Vector3d axis);
            resultRotation = Transform.Rotation(angle, axis, Point3d.Origin);

            Transform resultTransform = resultRotation;
            resultTransform.M03 = weightedTranslation.X;
            resultTransform.M13 = weightedTranslation.Y;
            resultTransform.M23 = weightedTranslation.Z;

            return resultTransform;
        }

        /// <summary>
        /// Custom Spherical Linear Interpolation (SLERP) for quaternions
        /// </summary>
        /// <param name="q1"></param>
        /// <param name="q2"></param>
        /// <param name="t"></param>
        /// <returns></returns>
        private static Quaternion Slerp(Quaternion q1, Quaternion q2, double t)
        {
            double dot = q1.A * q2.A + q1.B * q2.B + q1.C * q2.C + q1.D * q2.D;

            if (dot < 0.0) {
                q2 = new Quaternion(-q2.A, -q2.B, -q2.C, -q2.D);
                dot = -dot;
            }

            const double THRESHOLD = 0.9995;
            if (dot > THRESHOLD) {
                Quaternion result = new Quaternion(
                    q1.A + t * (q2.A - q1.A),
                    q1.B + t * (q2.B - q1.B),
                    q1.C + t * (q2.C - q1.C),
                    q1.D + t * (q2.D - q1.D)
                );
                result.Unitize();
                return result;
            }

            double theta0 = Math.Acos(dot);
            double theta = theta0 * t;

            double sinTheta = Math.Sin(theta);
            double sinTheta0 = Math.Sin(theta0);

            double s0 = Math.Cos(theta) - dot * sinTheta / sinTheta0;
            double s1 = sinTheta / sinTheta0;

            return new Quaternion(
                (s0 * q1.A) + (s1 * q2.A),
                (s0 * q1.B) + (s1 * q2.B),
                (s0 * q1.C) + (s1 * q2.C),
                (s0 * q1.D) + (s1 * q2.D)
            );
        }
    }
}
