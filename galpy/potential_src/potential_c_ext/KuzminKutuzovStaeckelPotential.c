#include <math.h>
#include <galpy_potentials.h>
//KuzminKutuzovStaeckelPotential
//3  arguments: amp, ac, Delta
double KuzminKutuzovStaeckelPotentialEval(double R,double Z, double phi,
				    double t,
				    struct potentialArg * potentialArgs){
  double * args= potentialArgs->args;
  //Get args
  double amp   = *args;
  double ac    = *(args+1);
  double Delta = *(args+2);
  //How does the code know in which order the args appear???????????? LogHaloPot has a different arg order in c and python.????????? Why is the get args in each function in LogHaloPot different?????
  //Coordinate transformation
  double gamma = Delta*Delta / (1.-ac*ac)
  double alpha = gamma - Delta*Delta
  double term  =     R*R + z*z - alpha - gamma;
  double discr = pow(R*R + z*z - Delta*Delta, 2.) + (4. * Delta*Delta * R*R);
  double l     = 0.5 * (term + sqrt(discr)); 
  double n     = 0.5 * (term - sqrt(discr));
  //Calculate potential
  return - amp /(sqrt(l) + sqrt(n));
}
double KuzminKutuzovStaeckelPotentialRforce(double R,double Z, double phi,
				      double t,
				      struct potentialArg * potentialArgs){
  double * args= potentialArgs->args;
  //Get args
  double amp   = *args;
  double ac    = *(args+1);
  double Delta = *(args+2);
  //Coordinate transformation
  double gamma = Delta*Delta / (1.-ac*ac);
  double alpha = gamma - Delta*Delta;
  double term  =     R*R + z*z - alpha - gamma;
  double discr = pow(R*R + z*z - Delta*Delta, 2.) + (4. * Delta*Delta * R*R);
  double l     = 0.5 * (term + sqrt(discr)); 
  double n     = 0.5 * (term - sqrt(discr));
  double dldR  = R * (1. + (R*R + z*z + Delta*Delta) / sqrt(discr));
  double dndR  = R * (1. - (R*R + z*z + Delta*Delta) / sqrt(discr));
  //Calculate Rforce
  double dVdl = 0.5/sqrt(l)/pow(sqrt(l)+sqrt(n),2.);
  double dVdn = 0.5/sqrt(n)/pow(sqrt(l)+sqrt(n),2.);
  return -(dldR * dVdl + dndR * dVdn);
}
double KuzminKutuzovStaeckelPotentialPlanarRforce(double R,double phi,
					    double t,
					    struct potentialArg * potentialArgs){
  double * args= potentialArgs->args;
  //Get args
  double amp   = *args;
  double ac    = *(args+1);
  double Delta = *(args+2);
  //Coordinate transformation (for z=0)
  double gamma = Delta*Delta / (1.-ac*ac);
  double alpha = gamma - Delta*Delta;
  double l     = R*R - alpha;
  double n     = -gamma;
  double dldR  = 2.*R;
  //Calculate Rforce
  double dVdl = 0.5/sqrt(l)/pow(sqrt(l)+sqrt(n),2.)
  return -dldR * dVdl;
}
double KuzminKutuzovStaeckelPotentialzforce(double R,double z,double phi,
				      double t,
				      struct potentialArg * potentialArgs){
  double * args= potentialArgs->args;
  //Get args
  double amp   = *args;
  double ac    = *(args+1);
  double Delta = *(args+2);
  //Coordinate transformation
  double gamma = Delta*Delta / (1.-ac*ac);
  double alpha = gamma - Delta*Delta;
  double term  =     R*R + z*z - alpha - gamma;
  double discr = pow(R*R + z*z - Delta*Delta, 2.) + (4. * Delta*Delta * R*R);
  double l     = 0.5 * (term + sqrt(discr)); 
  double n     = 0.5 * (term - sqrt(discr));
  double dldz  = z * (1. + (R*R + z*z - Delta*Delta) / sqrt(discr))
  double dndz  = z * (1. - (R*R + z*z - Delta*Delta) / sqrt(discr))
  //Calculate zforce
  double dVdl = 0.5/sqrt(l)/pow(sqrt(l)+sqrt(n),2.);
  double dVdn = 0.5/sqrt(n)/pow(sqrt(l)+sqrt(n),2.);
  return -(dldz * dVdl + dndz * dVdn);
}
double KuzminKutuzovStaeckelPotentialPlanarR2deriv(double R,double phi,
					     double t,
					     struct potentialArg * potentialArgs){
  double * args= potentialArgs->args;
  //Get args
  double amp   = *args;
  double ac    = *(args+1);
  double Delta = *(args+2);
  //Coordinate transformation (for z=0)
  double gamma  = Delta*Delta / (1.-ac*ac);
  double alpha  = gamma - Delta*Delta;
  double l      = R*R - alpha;
  double n      = -gamma;
  double dldR   = 2.*R;
  double d2ldR2 = 2.;
  //Calculate R2deriv
  double dVdl   = 0.5/sqrt(l)/pow(sqrt(l)+sqrt(n),2.);
  double d2Vdl2 = (-3.*sqrt(l)-sqrt(n)) / (4. * pow(l,1.5) * pow(sqrt(l)+sqrt(n),3.)
  return d2ldR2 * dVdl + dldR*dldr*d2Vdl2
}

